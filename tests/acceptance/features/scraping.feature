Feature: API de scraping
	Como consumidor de la API
	Quiero enviar una petición de scraping indicando una URL y selectores
	Para recibir un JSON con los elementos extraídos

	Scenario: Solicitar scraping de una página y recibir items
		Given el cuerpo de la petición con la URL "https://example.com" y los selectores "h1"
		When hago POST a "/scrape" con ese cuerpo
		Then la respuesta tiene el status 200
		And la respuesta contiene una clave "data" que es un diccionario con los selectores

