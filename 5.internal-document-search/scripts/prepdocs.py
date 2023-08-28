import argparse
from azure.identity import AzureDeveloperCliCredential
from azure.identity import ManagedIdentityCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from pypdf import PdfReader, PdfWriter
from glob import glob
import io
import os
import re

from typing import Dict, List, Tuple


# ログ出力用のクラス
class Logger:
	def __init__(self, verbose: bool):
		self.verbose = verbose

	def log(self, logging_message: str):
		if self.verbose:
			print(logging_message)


# 引数を読み込む関数
def read_argument() -> Tuple[Dict[str, str], Logger]:
	parser = argparse.ArgumentParser(
	description="Prepare documents by extracting content from PDFs, splitting content into sections, uploading to blob storage, and indexing in a search index.",
	epilog="Example: prepdocs.py '..\data\*' --storageaccount myaccount --container mycontainer --searchservice mysearch --index myindex -v"
	)
	parser.add_argument("files", help="Files to be processed")
	parser.add_argument("--storageaccount", help="Azure Blob Storage account name")
	parser.add_argument("--storagekey", required=False, help="Optional. Use this Azure Blob Storage account key instead of the current user identity to login (use az login to set current user for Azure)")
	parser.add_argument("--container", help="Azure Blob Storage container name")
	parser.add_argument("--tenantid", required=False, help="Optional. Use this to define the Azure directory where to authenticate)")
	parser.add_argument("--searchservice", help="Name of the Azure Cognitive Search service where content should be indexed (must exist already)")
	parser.add_argument("--searchkey", required=False, help="Optional. Use this Azure Cognitive Search account key instead of the current user identity to login (use az login to set current user for Azure)")
	parser.add_argument("--index", help="Name of the Azure Cognitive Search index where content should be indexed (will be created if it doesn't exist)")
	parser.add_argument("--formrecognizerservice", required=False, help="Optional. Name of the Azure Form Recognizer service which will be used to extract text, tables and layout from the documents (must exist already)")
	parser.add_argument("--formrecognizerkey", required=False, help="Optional. Use this Azure Form Recognizer account key instead of the current user identity to login (use az login to set current user for Azure)")
	parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
	parser.add_argument('--managedidentitycredential', action='store_true', help='Use Managed Identity (e.g., Cloud Shell) credentials')
	args = parser.parse_args()

	logger = Logger(args.verbose)

	return args, logger


# Azure Developer CLIの認証情報を取得する関数
def _get_azd_credential(tenantid: str):
	if tenantid is None:
		return AzureDeveloperCliCredential()
	else:
		return AzureDeveloperCliCredential(tenant_id=tenantid, process_timeout=60)


# 認証方法を決定する関数
def init_default_credential(managedidentitycredential: bool, searchkey: str, storagekey: str, tenantid: str):
	# --managedidentitycredentialオプションが指定されたとき
	if managedidentitycredential:
		return ManagedIdentityCredential()
	# keyが指定されないとき
	if searchkey is None or storagekey is None:
		azd_credential = _get_azd_credential(tenantid)
		return azd_credential
	# keyが指定されたとき
	else:
		return None


# Search Serviceの認証情報を取得する関数
def init_search_service_credential(service_name: str, secret_key: str, default_creds):
    if service_name is None:
        print("Error: Search service is not provided.")
        exit(1)
    if secret_key is None:
        return default_creds
    else:
        return AzureKeyCredential(secret_key)


# Form Recognizerの認証情報を取得する関数
def init_form_recognizer_credential(service_name: str, secret_key: str, default_creds):
    if service_name is None:
        print("Error: Azure Form Recognizer service is not provided. Please provide formrecognizerservice or use --localpdfparser for local pypdf parser.")
        exit(1)
    if secret_key is None:
        return default_creds
    else:
        return AzureKeyCredential(secret_key)


# Storage Accountの認証情報を取得する関数
def init_storage_credential(storage_account_name: str, secret_key: str, default_creds):
	if storage_account_name is None:
		print("Error: Storage account is not provided.")
		exit(1)
	if secret_key is None:
		return default_creds
	else:
		return secret_key


# PDFファイルからテキストを抽出する関数
def recognize_text_from_pdf(target_file_path: str, form_recognizer_name: str, form_recognizer_creds) -> List[Dict[str, str]]:
	form_recognizer_client = DocumentAnalysisClient(
		endpoint=f"https://{form_recognizer_name}.cognitiveservices.azure.com/",
		credential=form_recognizer_creds,
		headers={"x-ms-useragent": "azure-search-chat-demo/1.0.0"}
	)
	# ファイルを読み込み、テキストを抽出
	with open(target_file_path, "rb") as f:
		poller = form_recognizer_client.begin_analyze_document("prebuilt-layout", document = f)
	form_recognizer_results = poller.result()
	# ページごとにテキストを結合
	document_content_list = []
	target_file_name = os.path.basename(target_file_path)
	for page in form_recognizer_results.pages:
		page_content = "\n".join([line.content for line in page.lines])
		document_content_list.append({
			"id": re.sub("[^0-9a-zA-Z_-]","_",f"{target_file_name}-{page.page_number}"),
            "content": page_content,
            "category": None,
            "sourcepage": f"{os.path.splitext(target_file_name)[0]}-{page.page_number}.pdf",
            "sourcefile": target_file_name
		})
	return document_content_list


# Search Serviceのインデックスを作成する関数
def create_search_service_index(search_creds, search_service_name: str, index_name: str):
	search_service_index_client = SearchIndexClient(
		endpoint=f"https://{search_service_name}.search.windows.net/",
		credential=search_creds
	)
	# indexが登録済みの場合
	if index_name in search_service_index_client.list_index_names():
		print(f"Search index {index_name} already exists")
	else:
		semantic_config = SemanticConfiguration(
			name='default',
			prioritized_fields=PrioritizedFields(
				title_field=None,
				prioritized_content_fields=[SemanticField(field_name='content')]
			)
		)
		# id, content, category, sourcepage, sourcefileの5つのフィールドを持つindexを作成
		search_service_index = SearchIndex(
            name=index_name,
            fields=[
                SimpleField(name="id", type="Edm.String", key=True),
                SearchableField(name="content", type="Edm.String", analyzer_name="ja.microsoft"),
                SimpleField(name="category", type="Edm.String", filterable=True, facetable=True),
                SimpleField(name="sourcepage", type="Edm.String", filterable=True, facetable=True),
                SimpleField(name="sourcefile", type="Edm.String", filterable=True, facetable=True)
            ],
            semantic_settings=SemanticSettings(
                configurations=[semantic_config]
			)
        )
		try:
			search_service_index_client.create_index(search_service_index)
		except Exception as ex:
			print(f"Error creating search index {index_name}: {ex}")
			exit(1)


# search indexにドキュメントを追加する関数
def add_documents_to_index(
		search_service_name: str,
		index_name: str,
		search_creds,
		document_content_list: List[Dict[str, str]],
		logger: Logger
	):
	search_client = SearchClient(
		endpoint=f"https://{search_service_name}.search.windows.net/",
		index_name=index_name,
		credential=search_creds
	)
	# ドキュメントをindexに追加
	results = search_client.upload_documents(documents=document_content_list)
	n_success_docs = sum([1 for result in results if result.succeeded])
	logger.log(f"\tCreate Index Succeeded: {n_success_docs}/{len(results)} Pages")


# ドキュメントをblob storageにアップロードする関数
def upload_documents_to_blob_storage(
		blob_service_name: str,
		container_name: str,
		target_file_path: str,
		storage_creds,
		logger: Logger
	):

	blob_service_client = BlobServiceClient(
		account_url=f"https://{blob_service_name}.blob.core.windows.net",
		credential=storage_creds
	)
	container_client = blob_service_client.get_container_client(container_name)
	target_file_name = os.path.basename(target_file_path)
	# コンテナが存在しない場合は作成
	if not container_client.exists():
		container_client.create_container()

	# PDFファイルの場合
	if os.path.splitext(target_file_name)[1].lower() == ".pdf":
		reader = PdfReader(target_file_path)
		pages = reader.pages
		for idx, page in enumerate(pages):
			page_number = idx + 1
			logger.log(
				f"\tUploading blob for page {page_number} -> {os.path.splitext(target_file_name)[0]}-{page_number}.pdf"
			)
			# 1ページのPDFを切り出す
			single_page_pdf = io.BytesIO()
			writer = PdfWriter()
			writer.add_page(page)
			writer.write(single_page_pdf)
			single_page_pdf.seek(0)
			# blob storageにアップロード
			container_client.upload_blob(
				name=f"{os.path.splitext(target_file_name)[0]}-{page_number}.pdf",
				data=single_page_pdf,
				overwrite=True
			)
	# PDFファイル以外の場合
	else:
		print(f"Error: Must be a PDF file: {target_file_path}")
		exit(1)


# main実行関数
def main():
	# CLIから引数を取得
	args, logger = read_argument()

	logger.log("\nGetting credentials...")
	# 認証方法を定義
	default_creds = init_default_credential(
		managedidentitycredential=args.managedidentitycredential,
		searchkey=args.searchkey,
		storagekey=args.storagekey,
		tenantid=args.tenantid
	)

	# Search Serviceの認証情報を取得
	search_creds = init_search_service_credential(
		service_name=args.searchservice,
		secret_key=args.searchkey,
		default_creds=default_creds
	)

	# Form Recognizerの認証情報を取得
	form_recognizer_creds = init_form_recognizer_credential(
		service_name=args.formrecognizerservice,
		secret_key=args.formrecognizerkey,
		default_creds=default_creds
	)

	# Storage Accountの認証情報を取得
	storage_creds = init_storage_credential(
		storage_account_name=args.storageaccount,
		secret_key=args.storagekey,
		default_creds=default_creds
	)

	# Search Serviceのインデックスを作成
	logger.log("Creating search index...")
	create_search_service_index(search_creds, args.searchservice, args.index)

	for pdfFile in glob(args.files):
		# ファイルを読み込み、テキストを抽出
		logger.log(f"\nExtracting text from {os.path.basename(pdfFile)}...")
		document_content_list = recognize_text_from_pdf(
			pdfFile,
			args.formrecognizerservice, 
			form_recognizer_creds
		)

		# ドキュメントをindexに追加
		logger.log(f"Registering {os.path.basename(pdfFile)} to Search index...")
		add_documents_to_index(
			search_service_name=args.searchservice,
			index_name=args.index,
			search_creds=search_creds,
			document_content_list=document_content_list,
			logger=logger
		)

		# ドキュメントをblob storageにアップロード
		logger.log(f"Uploading {os.path.basename(pdfFile)} to Blob Storage...")
		upload_documents_to_blob_storage(
			blob_service_name=args.storageaccount,
			container_name=args.container,
			target_file_path=pdfFile,
			storage_creds=storage_creds,
			logger=logger
		)

	logger.log("\nTask completed")

main()
