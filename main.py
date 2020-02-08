import scrapy

def main():
    mvg_api = "https://www.mvg.de/api/fahrinfo/departure/de:09162:700"
    create_folder(data_folder)
    api_file = os.path.join(data_folder, "departures.p")
    lock = threading.Lock()
    threading.Thread(target=fe)
    content = list()
    start_up(mvg_api, api_file, lock)
    respObj = pickle.load(open(api_file, "rb"))
    i = 0
    refresh_counter = 0
    while True:
        if refresh_counter == 4:
            tempRespObj = load_data(api_file, lock)
            if "departures" in tempRespObj.keys() and len(tempRespObj["departures"]) > 0:
                respObj = tempRespObj
        if refresh_counter >= 45:
            start_data_fetch_thread(mvg_api, api_file, lock)
            refresh_counter = 0
        refresh_counter += 1
        min_list_flughafen_s_bahn = get_minutes(s8_to_airport, 3, respObj)
        min_list_city_s_bahn = get_minutes(s8_into_city, 3, respObj)
        for api_data in respObj["departures"]:
            destination, departure_time_display, delay = process_data(api_data)
            content.append([destination, departure_time_display, delay])
            i += 1
            if i > show_next_connections:
                break
        i = 0

        header = ["Richtung", "Minuten", "Verspätung"]
        print(tabulate(content, headers=header))
        print("")
        display.s_bahn_layout(min_list_flughafen_s_bahn, min_list_city_s_bahn)
 
        content = list()
        time.sleep(1)

if __name__ == "__main__":
    main()