// Copyright (c) Microsoft Corporation
// Licensed under the MIT license.

var gpt_loading_spinner = '<div id="openai_spinner" class="h-center"><div class="spinner-border text-success mb-2 loading-icon" role="status"></div><p class="mute text-s">Summarizing...</p></div>'

// Speech Recognition & Translation with Speech SDK
var SpeechSDK;
var recognizer;
var startAsyncButton = $("#startAsyncButton");
var stopAsyncButton = $("#stopAsyncButton");
var token = $("#azureToken").val();
var resourceId= $("#resourceId").val();
var speechRegion = $("#speechRegion").val();
var speechLang = $('select#speechLang').val();
var translateLang = $('select#translateLang').val();
var displaySpeech = $("#displaySpeech");
var displayTranslation = $("#displayTranslation");
var divRecognized = $('#divRecognized');
var divTranslated = $('#divTranslated');
var divOpenAICard = $('#divOpenAICard');
var divOpenAI = $('#divOpenAI');
var divOpenAISpinner = $('#divOepnAISpinner');
var speakerId = 'Speaker0';

// Update parameter selection
$("select#speechLang").change(function() {
    speechLang = $(this).children("option:selected").val();
});
$("select#translateLang").change(function() {
    translateLang = $(this).children("option:selected").val();
});
$("#token").change(function() {
    token = $(this).val();
});
$("#resourceId").change(function() {
    resourceId = $(this).val();
});
$("#speechRegion").change(function() {
    speechRegion = $(this).val();
});

// On DOM ready load SpeechSDK and start MediaRecorder
$(document).ready(function() {  
           
    // Get access token from server
    try {
        getToken();
    }
    catch(err) {
        $('#loading-message').text(err.message);
        return;
    }
 
    // Load Speech SDK
    if (!!window.SpeechSDK) {
        SpeechSDK = window.SpeechSDK;
        startAsyncButton.disabled = false;
        $('#now-loading').hide();
        $('#demo-container').show();
    }
    
    // Speech-to-text and Speech Translation from audio stream
    startAsyncButton.on("click", function(event) {

        // Fetch forms and check input validation (Speech/Language Key) 
        var forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function (form) {

            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        })

        // Toggle mic on/off button
        startAsyncButton.hide();
        stopAsyncButton.show();

        try {
            // Speech config
            authorizationToken = "aad#" + resourceId + "#" + token
            const speechConfig = SpeechSDK.SpeechTranslationConfig.fromAuthorizationToken(authorizationToken, speechRegion);
            
            // Set recognition properties
            speechConfig.speechRecognitionLanguage = speechLang;
            speechConfig.addTargetLanguage(translateLang);
            
            // Set CTS properties
            speechConfig.setProperty("f0f5debc-f8c9-4892-ac4b-90a7ab359fd2", "true");
            speechConfig.setProperty("ConversationTranscriptionInRoomAndOnline", "true");
            speechConfig.setProperty("DifferentiateGuestSpeakers", "true");
            speechConfig.setProperty("TranscriptionService_SingleChannel", "true");
            speechConfig.outputFormat = SpeechSDK.OutputFormat.Simple;

            // Audio config for Recognizer
            const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
            
            // Audio config for Transcriber
            const audioConfigCTS = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
            
            // CTS conversation and transcriber
            var conversation = SpeechSDK.Conversation.createConversationAsync(speechConfig, "myConversation");
            transcriber = new SpeechSDK.ConversationTranscriber(audioConfigCTS);
            
            // Initialize SpeechRecognizer
            recognizer = new SpeechSDK.TranslationRecognizer(speechConfig, audioConfig);
            recognizer.startContinuousRecognitionAsync(console.log('Recognizer session started'));

            // Initialize CTS transcriber
            transcriber.joinConversationAsync(conversation,
                function () {
                    transcriber.transcribing = onRecognizing;
                    transcriber.transcribed = onRecognized;
                    transcriber.canceled = onCanceled;
                    transcriber.sessionStarted = onSessionStarted;
                    transcriber.sessionStopped = onSessionStopped;

                    transcriber.startTranscribingAsync(
                        function () {                                                            
                        },
                        function (err) {
                            console.trace("err - starting transcription: " + err);
                        }
                    );
                },
            );
        }
        catch(err) {
            displaySpeech.text(err);
            return;
        }

        // (1) Speech Recognizer (for all Recognizing events)
        recognizer.recognizing = (s, e) => {
            var current_time = new Date();
            time_label = current_time.toLocaleString('en-US', { timeStyle: 'medium', hour12: false});
            
            // Update display window with in-progress recognition & translation
            displaySpeech.html(divRecognized.val() + '['+ time_label +'] ' +e.result.text);
            displayTranslation.html(divTranslated.val() + '['+ time_label +'] ' + e.result.translations.get(translateLang));
        };

        // (2) CTS Transcriber (for Transcribed event only)
        function onRecognizing(s, e) {
            // Basically do nothing
            // This is a placeholder
        };

        /***
         * (3) CTS only works in centralus, eastasia, eastus and westeurope. if this will be available in all regions, we can use this instead of recognized event.
         * https://learn.microsoft.com/ja-jp/azure/cognitive-services/speech-service/how-to-use-conversation-transcription?pivots=programming-language-javascript
        ***/
        function onRecognized(s, e) {                
            /*
            if (e.result.reason == SpeechSDK.ResultReason.RecognizedSpeech || e.result.reason == SpeechSDK.ResultReason.TranslatedSpeech) {
                var current_time = new Date();
                time_label = current_time.toLocaleString('en-US', { timeStyle: 'medium', hour12: false});

                // append newly recognized phrase to the recognized list
                if (e.result.text) {
                    if (e.result.speakerId == 'Unidentified') {
                        speakerId = 'Speaker0'
                    }
                    else {
                        speakerId = e.result.speakerId.replace('Guest_','Speaker')
                    }
                    divRecognized.append('['+ speakerId +'] '+e.result.text+'\n');
                    displaySpeech.html(divRecognized.val());
                }
            }
            */
        };

        // (3') Speech Recognizer (for Translated event only)
        recognizer.recognized = (s, e) => {
            if (e.result.reason == SpeechSDK.ResultReason.RecognizedSpeech || e.result.reason == SpeechSDK.ResultReason.TranslatedSpeech) {
                var current_time = new Date();
                time_label = current_time.toLocaleString('en-US', { timeStyle: 'medium', hour12: false});
                            
                if (e.result.text) {
                    // Update display window with in-progress recognition & translation
                    divRecognized.append('['+ time_label +'] '+e.result.text+'\n');
                    displaySpeech.html(divRecognized.val());
                    displaySpeech.scrollTop(displaySpeech[0].scrollHeight - displaySpeech.height());
                }

                if (e.result.text) {
                    langCode = speechLang.substring(0, speechLang.indexOf('-'));
                    runSentimentAnalysis(e.result.text, langCode);
                }
                
                // append newly translated phrase to the translated list
                if (e.result.translations.get(translateLang)) {
                    divTranslated.append('['+ time_label +'] '+e.result.translations.get(translateLang)+'\n');
                    displayTranslation.html(divTranslated.val());
                    displayTranslation.scrollTop(displayTranslation[0].scrollHeight - displayTranslation.height());
                }
            }
        };

        
        // CTS Event handlers
        function onCanceled (s, e) {
            console.log(`Transcriber CANCELED: Reason=${e.reason}`);
            if (e.reason == sdk.CancellationReason.Error) {
                console.log(`"Transcriber CANCELED: ErrorCode=${e.errorCode}`);
                console.log(`"Transcriber CANCELED: ErrorDetails=${e.errorDetails}`);
                console.log("Transcriber CANCELED: Did you set the speech resource key and region values?");
            }
            transcriber.close();
            transcriber = undefined;
        };

        function onSessionStopped(s, e) {
            console.log("Transcriber session stopped");
            // transcriber.close();
        };
        
        function onSessionStarted(s, e) {
            console.log("Transcriber session started");
        }

        // Recognizer event handlers
        recognizer.canceled = (s, e) => {
            console.log(`Recognizer CANCELED: Reason=${e.reason}`);
            if (e.reason == sdk.CancellationReason.Error) {
                console.log(`"Recognizer CANCELED: ErrorCode=${e.errorCode}`);
                console.log(`"Recognizer CANCELED: ErrorDetails=${e.errorDetails}`);
                console.log("Recognizer CANCELED: Did you set the speech resource key and region values?");
            }
            recognizer.stopContinuousRecognitionAsync();
        };

        recognizer.sessionStopped = (s, e) => {
            console.log("Recognizer session stopped");
            recognizer.stopContinuousRecognitionAsync();
        };
            
        
        // Stop Button
        stopAsyncButton.on("click", function () {
            recognizer.stopContinuousRecognitionAsync();
            transcriber.close();
            transcriber = undefined;
            startAsyncButton.show();
            stopAsyncButton.hide();
            runGPT();
        });

    });
});

// Get Speech Service access token from backend service
function getToken() {
    $.ajax({
        url: $SCRIPT_ROOT + '/token',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        async: false
    }).done(function(response) {
        if (response.status == 'OK') {
            token = response.azure_token;
            if(token==undefined)
                throw new Error("Error : Managed ID is not cofigured properly.");

            resourceId = response.resource_id;
            if(resourceId==undefined)
                throw new Error("Error : environment variable [STT_RESOURCE_ID] is not defined in backend service.");

            speechRegion= response.speech_region;
            if(speechRegion==undefined)
                throw new Error("Error : environment variable [STT_REGION] is not defined in backend service.");
        }
        else {
            throw new Error(response.error);
        }
    });
};

// Call OpenAI
function runGPT() {
    if ($("#displaySpeech").val().length==0) {
        return;
    }

    var form_data = JSON.stringify({
        transcription: $("#displaySpeech").val()
      });
      $.ajax({
        url: $SCRIPT_ROOT + '/gpt',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: form_data,
        dataType: 'json',
        beforeSend: function() {
            divOpenAI.html(gpt_loading_spinner);
            divOpenAICard.addClass('v-center');
        }
      }).done(function(response) {
        divOpenAICard.removeClass('v-center');
        if (response.status == 'OK') {
            var entities = response.q3;
            var arrayLength = entities.length;
            var entityHTML = '';
            for (var i = 0; i < arrayLength; i++) {
                entityHTML += `<span class="badge badge-success rounded-pill text-light px-3 mb-1 me-1 text-s lh-base">${entities[i]}</span>`;
            }
            divOpenAI.html(`
            <div class="h5 pb-1 text-gray-800 text-m lh-base fw-light" style="text-align: start;">
                <p class="mute text-m">${response.q1}</p>
                <h6>Sentiment Score</h6>
                <p>${response.q2}</p>
                <h6>Key Entities</h6>
                <p>${entityHTML}</p>
                <h6>Topic</h6>
                <p>${response.q4}</p>
            </div>
            `);
        } else {
          divOpenAI.text(response.error);
        }
      });
};

// Call Text Analytics SentimentAnalysis
function runSentimentAnalysis(text, langCode) {    
    var payload = { 
        documents: [
            { id: "1", language: langCode, text: text}
        ]
    };
   
    $.ajax({
        url: $SCRIPT_ROOT + '/sentiment',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(payload),
        dataType: 'json',
    }).done(function(response) {
        if (response.status == 'OK') {
            normalized_score = getNormalizedScore( response.confidence_scores[0]);

            // Ppush label & sentiment score to chart for re-rendering
            var current_time = new Date();
            time_label = current_time.toLocaleString('ja-JP', { timeStyle: 'medium'});
            time_labels.push(time_label);
            score_values.push(normalized_score);
            addData(myChart, time_label, normalized_score);
            
            // Keep chart neatly at most recent 15 points
            if (score_values.length > 15) {
                shiftData(myChart);
            }
        }
        else {
            throw new Error(response.error[0]);
        }
    });
};

function getNormalizedScore(scoreArray) {
    let max_score = Math.max(...Object.values(scoreArray))
    let max_sentiment = Object.keys(scoreArray).filter(key => scoreArray[key]==max_score)[0];
    if (max_sentiment == "positive") return max_score;
    else if (max_sentiment == "negative") return max_score * -1;
    else return (scoreArray.positive >= scoreArray.negative) ? scoreArray.positive : scoreArray.negative * -1;
}

// Chart.js
var time_labels = [];
var score_values = [];

// Gradient color (green: positive, yellow: neutral, red: negative)
function getGradient(ctx, chartArea, alpha) {
    let width, height, gradient;
    const chartWidth = chartArea.right - chartArea.left;
    const chartHeight = chartArea.bottom - chartArea.top;
    if (gradient === null || width !== chartWidth || height !== chartHeight) {
        // Create the gradient because this is either the first render
        // or the size of the chart has changed
        width = chartWidth;
        height = chartHeight;
        gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
        gradient.addColorStop(0, `rgb(255, 99, 132, ${alpha})`);
        gradient.addColorStop(0.3, `rgb(255, 205, 86, ${alpha})`);
        gradient.addColorStop(1, `rgb(75, 192, 192, ${alpha})`);
    }
    return gradient;
}

// Chart data (sentiment scores)
var data = {
    labels: [],
    datasets: [{
        label: 'Sentiment Score',
        data: [],
        borderWidth: 6,
        pointRadius: 3,
        fill: 'origin',
        backgroundColor: function(context) {
            const chart = context.chart;
            const {ctx, chartArea} = chart;
            if (!chartArea) {
                return null;
            }
            return getGradient(ctx, chartArea, .3);
        },
        // borderColor: '#333',
        borderColor: function(context) {
            const chart = context.chart;
            const {ctx, chartArea} = chart;
            if (!chartArea) {
                return null;
            }
            return getGradient(ctx, chartArea, 1);
        },
    }]
};

// Chart config & options
const config = {
    type: 'line',
    data: data,
    options: {
        elements: {
            line: {
                tension: 0.3
            },
        },
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: 'リアルタイム感情分析'
            },
        },
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                display: true,
                title: {
                    display: false,
                    text: 'Sentiment Score'
                },
                suggestedMin: -1,
                suggestedMax: 1,
                grid: {
                    display: true,
                    borderWidth: 2,
                    borderDash: [3, 3],
                    color: '#aaa',
                    borderDashOffset: 0,
                }
            },
            x: {
                grid: {
                    display: true,
                    borderWidth: 2,
                    borderDash: [3, 3],
                    color: '#aaa',
                    borderDashOffset: 0,
                }
            } 
        }
    }
};

// Render chart
const myChart = new Chart($('#myChart'), config);

// Function for pushing & removing data
function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();
}

function shiftData(chart) {
    chart.data.labels.shift();
    chart.data.datasets.forEach((dataset) => {
        dataset.data.shift();
    });
    chart.update();
}
