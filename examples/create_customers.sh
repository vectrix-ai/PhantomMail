#!/bin/bash

# API endpoint
API_URL="https://mpl-backend-dev.vectrix.app/api/v1/customers/"

# Function to send POST request
send_customer() {
    local customer_data="$1"
    echo "Sending customer: $(echo "$customer_data" | jq -r '.name')"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$customer_data")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        echo "✓ Success: $(echo "$body" | jq -r '.customer_id // .id // "Created"')"
    else
        echo "✗ Failed with status $http_code: $body"
    fi
    echo "---"
}

# Customer data
customers=(
'{"customer_id":"VANDERMEER-001","name":"Van Der Meer Logistics B.V.","primary_email":"info@vandermeer-log.nl","primary_phone":"+31 10 414 5678","vat_number":"NL823456789B01","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+31 10 414 5678"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Havenstraat 45","street2":"","city":"Rotterdam","postal_code":"3011 XH","country_code":"NL"},"is_active":true}'

'{"customer_id":"BRADWICK-001","name":"Bradwick Materials Ltd","primary_email":"transport@bradwick.co.uk","primary_phone":"+44 20 7474 8900","vat_number":"GB123456789","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"GBP"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+44 20 7474 8900"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"82 Victoria Road","street2":"","city":"London","postal_code":"E16 3PQ","country_code":"GB"},"is_active":true}'

'{"customer_id":"NORDVIK-001","name":"Nordvik Paper AB","primary_email":"logistics@nordvikpaper.se","primary_phone":"+46 31 750 2300","vat_number":"SE559876543201","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"SEK"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+46 31 750 2300"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Industrivägen 23","street2":"","city":"Gothenburg","postal_code":"411 38","country_code":"SE"},"is_active":true}'

'{"customer_id":"VERMEULEN-001","name":"Vermeulen Transport","primary_email":"planning@vermeulen.be","primary_phone":"+32 3 231 4567","vat_number":"BE0876543210","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 3 231 4567"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Rue du Port 156","street2":"","city":"Antwerp","postal_code":"2000","country_code":"BE"},"is_active":true}'

'{"customer_id":"CASTELLANO-001","name":"Grupo Castellano S.L.","primary_email":"transporte@grupocastellano.es","primary_phone":"+34 96 337 8900","vat_number":"ES12345678A","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+34 96 337 8900"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Calle del Puerto 78","street2":"","city":"Valencia","postal_code":"46021","country_code":"ES"},"is_active":true}'

'{"customer_id":"RICHTER-001","name":"Richter Chemie GmbH","primary_email":"logistik@richter-chemie.de","primary_phone":"+49 40 3742 1500","vat_number":"DE234567891","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+49 40 3742 1500"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Hafenallee 234","street2":"","city":"Hamburg","postal_code":"20457","country_code":"DE"},"is_active":true}'

'{"customer_id":"KOWALSKI-001","name":"Kowalski Dystrybucja Sp. z o.o.","primary_email":"transport@kowalski-dyst.pl","primary_phone":"+48 22 654 3210","vat_number":"PL5263456789","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"PLN"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+48 22 654 3210"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"ul. Magazynowa 67","street2":"","city":"Warsaw","postal_code":"00-801","country_code":"PL"},"is_active":true}'

'{"customer_id":"MORETTI-001","name":"Gruppo Moretti S.r.l.","primary_email":"spedizioni@gruppomoretti.it","primary_phone":"+39 010 234 5678","vat_number":"IT12345678901","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+39 010 234 5678"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Via del Porto 89","street2":"","city":"Genoa","postal_code":"16126","country_code":"IT"},"is_active":true}'

'{"customer_id":"DEBRUIJN-001","name":"De Bruijn Retail B.V.","primary_email":"warehouse@debruijn.nl","primary_phone":"+31 20 789 4321","vat_number":"NL856789012B02","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+31 20 789 4321"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Logistiekweg 112","street2":"","city":"Amsterdam","postal_code":"1014 BV","country_code":"NL"},"is_active":true}'

'{"customer_id":"STEINBACH-001","name":"Steinbach Pharma AG","primary_email":"versand@steinbach-pharma.at","primary_phone":"+43 1 234 5678","vat_number":"AT123456789","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+43 1 234 5678"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Industriestraße 45","street2":"","city":"Vienna","postal_code":"1220","country_code":"AT"},"is_active":true}'

'{"customer_id":"PEMBERTON-001","name":"Pemberton Freight Ltd","primary_email":"bookings@pembertonfreight.com","primary_phone":"+44 1304 240 500","vat_number":"GB987654321","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"GBP"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+44 1304 240 500"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Maritime House, Dock Street","street2":"","city":"Dover","postal_code":"CT16 1LB","country_code":"GB"},"is_active":true}'

'{"customer_id":"DUBOIS-001","name":"Dubois Granulats SARL","primary_email":"transport@dubois-granulats.fr","primary_phone":"+33 2 35 42 7890","vat_number":"FR78901234567","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+33 2 35 42 7890"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"12 Quai des Marchands","street2":"","city":"Le Havre","postal_code":"76600","country_code":"FR"},"is_active":true}'

'{"customer_id":"BALTIKA-001","name":"Baltika Metals UAB","primary_email":"logistics@baltikametals.lt","primary_phone":"+370 46 397 000","vat_number":"LT123456789012","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+370 46 397 000"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Uosto g. 34","street2":"","city":"Klaipeda","postal_code":"91246","country_code":"LT"},"is_active":true}'

'{"customer_id":"KELLER-001","name":"Keller Logistics AG","primary_email":"dispatch@keller-log.ch","primary_phone":"+41 44 256 8900","vat_number":"CH123456789","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"CHF"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+41 44 256 8900"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Bahnhofstrasse 78","street2":"","city":"Zurich","postal_code":"8001","country_code":"CH"},"is_active":true}'

'{"customer_id":"VANHOUTEN-001","name":"Van Houten Bouwstoffen B.V.","primary_email":"transport@vanhouten-bouw.nl","primary_phone":"+31 40 290 1234","vat_number":"NL890123456B01","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+31 40 290 1234"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Distributiecentrum 23","street2":"","city":"Eindhoven","postal_code":"5652 AC","country_code":"NL"},"is_active":true}'

'{"customer_id":"COPPENS-001","name":"Coppens Chemical N.V.","primary_email":"logistics@coppens-chem.be","primary_phone":"+32 89 36 4500","vat_number":"BE0456789123","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 89 36 4500"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Industrieweg 156","street2":"","city":"Genk","postal_code":"3600","country_code":"BE"},"is_active":true}'

'{"customer_id":"PSZ-001","name":"Port Services Zeebrugge N.V.","primary_email":"operations@psz.be","primary_phone":"+32 50 55 6789","vat_number":"BE0567891234","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 50 55 6789"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Kustlaan 89","street2":"","city":"Zeebrugge","postal_code":"8380","country_code":"BE"},"is_active":true}'

'{"customer_id":"DELACROIX-001","name":"Delacroix Pharma S.A.","primary_email":"expedition@delacroix-pharma.be","primary_phone":"+32 2 640 8900","vat_number":"BE0678912345","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 2 640 8900"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Avenue Louise 234","street2":"","city":"Brussels","postal_code":"1050","country_code":"BE"},"is_active":true}'

'{"customer_id":"APM-001","name":"Automotive Parts Mechelen N.V.","primary_email":"logistics@apm-parts.be","primary_phone":"+32 15 29 3456","vat_number":"BE0789123456","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 15 29 3456"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Antwerpsesteenweg 78","street2":"","city":"Mechelen","postal_code":"2800","country_code":"BE"},"is_active":true}'

'{"customer_id":"TERMINALNOORD-001","name":"Terminal Noordzee N.V.","primary_email":"planning@terminal-noordzee.be","primary_phone":"+32 3 541 7890","vat_number":"BE0891234567","status":"active","external_ids":{"legacy_id":"","erp_id":""},"financial_info":{"iban":"","bic":"","currency":"EUR"},"contact_info":{"secondary_emails":[],"mobile_numbers":[],"telephone_numbers":["+32 3 541 7890"],"contact_person":""},"business_info":{"customer_name2":"","department_name":"","remark":"","is_blocked":false},"location_info":{"street1":"Noorderlaan 147","street2":"","city":"Antwerp","postal_code":"2030","country_code":"BE"},"is_active":true}'
)

# Send each customer
echo "Starting customer creation..."
echo "=========================="

for customer in "${customers[@]}"; do
    send_customer "$customer"
    sleep 0.5  # Small delay between requests to avoid rate limiting
done

echo "=========================="
echo "Customer creation complete!"