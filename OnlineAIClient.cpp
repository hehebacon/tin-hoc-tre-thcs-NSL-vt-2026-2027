#include "OnlineAIClient.h"
#include "config.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

static String jsonEscape(const String& input) {
    String out;
    for (size_t i=0;i<input.length();++i) {
        const char c=input[i];
        if(c=='"') out += "\\\"";
        else if(c=='\\') out += "\\\\";
        else if(c=='\n') out += "\\n";
        else if(c=='\r') out += "\\r";
        else out += c;
    }
    return out;
}

static String extractGeminiText(const String& json) {
    const String key="\"text\":\"";
    int p=json.indexOf(key);
    if(p<0) return "";
    p += key.length();
    String out;
    bool escaped=false;
    for(;p<(int)json.length();++p) {
        char c=json[p];
        if(escaped) {
            if(c=='n') out+='\n';
            else if(c=='r') out+='\r';
            else out+=c;
            escaped=false;
        } else if(c=='\\') escaped=true;
        else if(c=='"') break;
        else out+=c;
    }
    return out;
}

void OnlineAIClient::begin() {
    lastOnline=false;
    error="";
}

bool OnlineAIClient::configured() const {
    return strlen(GEMINI_API_KEY)>0 && strlen(GEMINI_MODEL)>0;
}

bool OnlineAIClient::online() const { return lastOnline; }
const String& OnlineAIClient::lastError() const { return error; }

OnlineAIResult OnlineAIClient::ask(const String& prompt) const {
    lastOnline=false;
    error="";
    OnlineAIResult result;

    if(!configured()) {
        error="GEMINI_API_KEY not configured";
        result.text=error;
        return result;
    }
    if(WiFi.status()!=WL_CONNECTED) {
        error="WiFi internet unavailable";
        result.text=error;
        return result;
    }

    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;
    const String url=String("https://generativelanguage.googleapis.com/v1beta/models/")+
                     GEMINI_MODEL+":generateContent";

    if(!http.begin(client,url)) {
        error="HTTP begin failed";
        result.text=error;
        return result;
    }

    http.addHeader("Content-Type","application/json");
    http.addHeader("x-goog-api-key",GEMINI_API_KEY);

    const String body=String("{\"contents\":[{\"parts\":[{\"text\":\"")+
                      jsonEscape(prompt)+
                      "\"}]}]}";

    const int code=http.POST(body);
    result.httpCode=code;
    const String response=http.getString();
    http.end();

    if(code<200 || code>=300) {
        error="Gemini HTTP "+String(code);
        result.text=error;
        return result;
    }

    result.text=extractGeminiText(response);
    if(!result.text.length()) {
        error="Gemini returned no text";
        result.text=error;
        return result;
    }

    lastOnline=true;
    result.ok=true;
    return result;
}
