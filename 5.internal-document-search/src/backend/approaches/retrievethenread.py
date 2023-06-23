import openai
from approaches.approach import Approach
from approaches.chatlogging import write_chatlog, ApproachType
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from text import nonewlines

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class RetrieveThenReadApproach(Approach):

    template = \
"You are an intelligent assistant helping Contoso Inc employees with their healthcare plan questions and employee handbook questions. " + \
"Use 'you' to refer to the individual asking the questions even if they ask with 'I'. " + \
"Answer the following question using only the data provided in the sources below. " + \
"For tabular information return it as an html table. Do not return markdown format. "  + \
"Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. " + \
"If you cannot answer using the sources below, say you don't know. " + \
"""

###
Question: 'What is the deductible for the employee plan for a visit to Overlake in Bellevue?'

Sources:
info1.txt: deductibles depend on whether you are in-network or out-of-network. In-network deductibles are $500 for employee and $1000 for family. Out-of-network deductibles are $1000 for employee and $2000 for family.
info2.pdf: Overlake is in-network for the employee plan.
info3.pdf: Overlake is the name of the area that includes a park and ride near Bellevue.
info4.pdf: In-network institutions include Overlake, Swedish and others in the region

Answer:
In-network deductibles are $500 for employee and $1000 for family [info1.txt] and Overlake is in-network for the employee plan [info2.pdf][info4.pdf].

###
Question: '{q}'?

Sources:
{retrieved}

Answer:
"""

    def __init__(self, search_client: SearchClient, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, openai_deployment, gpt_model, user_name: str, q: str, overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semanticCaptions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("excludeCategory") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

        if overrides.get("semanticRanker"):
            r = self.search_client.search(q, 
                                          filter=filter,
                                          query_type=QueryType.SEMANTIC, 
                                          query_language="en-us", 
                                          query_speller="lexicon", 
                                          semantic_configuration_name="default", 
                                          top=top, 
                                          query_caption="extractive|highlight-false" if use_semantic_captions else None)
        else:
            r = self.search_client.search(q, filter=filter, top=top)
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        max_tokens = gpt_model.get("max_tokens")
        encoding = gpt_model.get("encoding")

        prompt = (overrides.get("promptTemplate") or self.template).format(q=q, retrieved=content)

        # input tokens + output tokens < max tokens of the model
        token_length = len(encoding.encode(prompt))
        if max_tokens > token_length + 1:
            max_tokens = max_tokens - (token_length + 1)

        completion = openai.Completion.create(
            engine=openai_deployment, 
            prompt=prompt, 
            temperature=float(overrides.get("temperature")) or 0.3, 
            max_tokens=max_tokens, 
            n=1, 
            stop=["\n"])
        
        result = completion.choices[0].text

        write_chatlog(ApproachType.Ask, user_name, 0, q, result)

        return {"data_points": results, "answer": result, "thoughts": f"Question:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}
