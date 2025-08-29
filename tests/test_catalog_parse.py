import pytest
import requests

BASE_URL = "http://localhost:8000/api"


def test_parse_and_get_products():

    post_url = f"{BASE_URL}/catalogs/parse-products/by-code/2649"
    print(f"\nОтправка POST-запроса на: {post_url}")

    try:
        post_response = requests.post(post_url)
        post_response.raise_for_status()
        print(f"Статус ответа POST: {post_response.status_code}")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Ошибка при выполнении POST-запроса: {e}")

    get_url = f"{BASE_URL}/products?limit=10"
    print(f"\nОтправка GET-запроса на: {get_url}")

    try:
        get_response = requests.get(get_url)
        get_response.raise_for_status()
        products = get_response.json()

        print("\n--- Полученные продукты (первые 10) ---")
        assert products, "Ответ на GET-запрос не должен быть пустым"

        import json

        print(json.dumps(products, indent=2, ensure_ascii=False))
        print("----------------------------------------")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Ошибка при выполнении GET-запроса: {e}")
