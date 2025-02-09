#include <iostream>
#include <iomanip>
#include <ctime>
#include <csignal>
#include <thread>
#include <chrono>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace std;

volatile sig_atomic_t exit_flag = 0;

void signal_handler(int signum) {
    cout << "\n[INFO] Received signal: " << signum << " (";
    switch (signum) {
        case SIGINT: cout << "SIGINT"; break;
        case SIGTERM: cout << "SIGTERM"; break;
        default: cout << "Unknown"; break;
    }
    cout << ")\n";
    exit_flag = 1;
}

size_t write_callback(void* contents, size_t size, size_t nmemb, string* output) {
    size_t total_size = size * nmemb;
    output->append((char*)contents, total_size);
    return total_size;
}

json get_weather() {
    const string url = "https://api.open-meteo.com/v1/forecast?latitude=25.0585178&longitude=121.6532539" 
                       "&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weathercode"
                       "&timezone=Asia/Taipei";
    
    CURL* curl = curl_easy_init();
    if (!curl) {
        cerr << "[ERROR] Failed to initialize CURL" << endl;
        return json();
    }
    
    string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    
    if (res != CURLE_OK) {
        cerr << "[ERROR] Failed to fetch weather data: " << curl_easy_strerror(res) << endl;
        return json();
    }
    
    return json::parse(response, nullptr, false);
}

string format_time(time_t raw_time) {
    struct tm* time_info = localtime(&raw_time);
    stringstream ss;
    ss << put_time(time_info, "%Y/%b/%d %H:%M:%S");
    return ss.str();
}

string get_weather_description(int code) {
    switch (code) {
        case 0: return "Clear sky";
        case 1: case 2: case 3: return "Partly cloudy";
        case 45: case 48: return "Fog";
        case 51: case 53: case 55: return "Drizzle";
        case 61: case 63: case 65: return "Rain";
        case 71: case 73: case 75: return "Snow";
        case 80: case 81: case 82: return "Rain showers";
        case 95: case 96: case 99: return "Thunderstorm";
        default: return "Unknown";
    }
}

int main() {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    time_t next_weather_update = time(nullptr) - 1;
    json weather_data;
    
    while (!exit_flag) {
        time_t now = time(nullptr);
        cout << "\r[Current Time] " << format_time(now) << flush;
        
        if (now >= next_weather_update) {
            cout << "\n[INFO] Updating weather data..." << endl;
            weather_data = get_weather();
            next_weather_update = now + 3600;
            
            if (!weather_data.empty() && weather_data.contains("hourly")) {
                auto& hourly = weather_data["hourly"];
                vector<string> times = hourly["time"].get<vector<string>>();
                size_t index = 0;
                while (index < times.size()) {
                    struct tm tm = {};
                    strptime(times[index].c_str(), "%Y-%m-%dT%H:%M", &tm);
                    time_t forecast_time = mktime(&tm);
                    if (forecast_time >= now) break;
                    ++index;
                }
                
                cout << "[Next 12 Hours Forecast]:" << endl;
                for (size_t i = 0; i < 12 && (index + i) < times.size(); ++i) {
                    size_t idx = index + i;
                    int weather_code = hourly["weathercode"][idx];
                    cout << "  " << times[idx] << ": "
                         << hourly["temperature_2m"][idx] << "°C, "
                         << "Humidity: " << hourly["relative_humidity_2m"][idx] << "%, "
                         << "Precipitation: " << hourly["precipitation_probability"][idx] << "%, "
                         << "Condition: " << get_weather_description(weather_code) << endl;
                }
            }
        }
        
        this_thread::sleep_for(chrono::seconds(1));
    }
    
    cout << "\n[INFO] Exiting..." << endl;
    return 0;
}

