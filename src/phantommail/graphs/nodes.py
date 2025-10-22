import os
import random
from importlib import resources

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI

from phantommail.fakers.complaint import FakeComplaint
from phantommail.fakers.declaration import DeclarationGenerator
from phantommail.fakers.price_request import PriceRequestGenerator
from phantommail.fakers.question import TransportQuestionGenerator
from phantommail.fakers.random_promotional import RandomPromotionalGenerator
from phantommail.fakers.transport import TransportOrderGenerator
from phantommail.fakers.update_order import UpdateOrderGenerator
from phantommail.fakers.waiting_costs import WaitingCostsGenerator
from phantommail.graphs.state import FakeEmailState
from phantommail.helpers.html_to_pdf import create_pdf
from phantommail.logger import setup_logger
from phantommail.models.email import Email, FullEmail
from phantommail.send_email import send

logger = setup_logger(__name__)


class GraphNodes:
    """The nodes for the fake email graph."""

    def __init__(self):
        """Initialize the graph nodes."""
        self.llm = ChatVertexAI(
            model="gemini-2.5-pro",
            temperature=0.5,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "manuport-mpl"),
        )

    def email_types(self, state: FakeEmailState, config):
        """Get the email types."""
        types = [
            "order",
            "question",
            "complaint",
            "declaration",
            "price_request",
            "waiting_costs",
            "update_order",
            "random",
        ]

        if "email_type" in state and state["email_type"] in types:
            return state["email_type"]

        return random.choice(types)

    async def generate_declaration(self, state: FakeEmailState, config):
        """Generate a fake customs declaration email."""
        declaration_generator = DeclarationGenerator()
        declaration = declaration_generator.generate_declaration().model_dump()

        logger.info(f"Generated customs declaration: {declaration}")

        example_number = random.randint(1, 2)

        # Read example templates
        email_html = (
            resources.files("phantommail.examples")
            .joinpath(f"customs_{example_number}_email.html")
            .read_text()
        )

        pdf_html = (
            resources.files("phantommail.examples")
            .joinpath(f"customs_{example_number}_pdf.html")
            .read_text()
        )

        # Format declaration details for use in prompts
        declaration_details = f"""
        ## Declaration details:
        - MRN: {declaration["mrn"]}
        - Declaration type: {declaration["declaration_type"]}
        - Reference number: {declaration["reference_number"]}
        - Total packages: {declaration["total_packages"]}
        - Items count: {declaration["items_count"]}
        
        ## Exporter details:
        - Company name: {declaration["exporter"]["name"]}
        - EORI/VAT number: {declaration["exporter"]["eori_number"]}
        - Address: {declaration["exporter"]["address"]}

        ## Importer details:
        - Company name: {declaration["importer"]["name"]}
        - EORI/VAT number: {declaration["importer"]["eori_number"]}
        - Address: {declaration["importer"]["address"]}

        ## Transport details:
        - Transport mode: {declaration["transport_info"]["transport_mode"]}
        - Place of loading: {declaration["transport_info"]["place_of_loading"]}
        - Arrival transport: {declaration["transport_info"]["arrival_transport"]}
        - Border transport: {declaration["transport_info"]["border_transport"]}

        ## Goods details:
        {chr(10).join([f"        - Item {item['item_number']}: {item['description_of_goods'] or 'Various goods'} ({item['packages'] or 0} packages, {item['gross_mass_kg'] or 0}kg)" for item in declaration["items"]])}

        ## Valuation:
        - Invoice currency: {declaration["invoice_currency"]}
        - Invoice value: {declaration["invoice_value"]}
        - Acceptance date: {declaration["acceptance_date_time"]}
        - Status: {declaration["declaration_status"]}
        """

        prompt = f"""Generate a fake customs declaration email based on the following data.
        
        IMPORTANT: Replace ALL references in BOTH the email HTML and PDF HTML templates with the actual data:
        - Replace all MRN numbers, company names, addresses, contact details with the declaration information
        - Replace dates, values, and goods descriptions with realistic values based on the declaration
        - Replace any placeholder text with appropriate content based on the customs declaration
        - Ensure both the email and PDF appear to come from the exporter company
        - Make sure the PDF contains detailed customs information matching the declaration
        - Don't put customs declaration in the subject but make it very abstract"
        
        The customs declaration is being sent to:
        Vectrans NV
        Kipdorpbrug 1
        2000 Antwerpen
        VAT: BE 1234.567.89

        Declaration details:
        {declaration_details}

        Create an email body and attachment in the following style:
        <body_html>
        {email_html}
        </body_html>

        <attachment_html>
        {pdf_html}
        </attachment_html>
        """

        llm_with_tools = self.llm.with_structured_output(Email)

        response = await llm_with_tools.ainvoke(
            [
                HumanMessage(content=prompt),
            ]
        )

        response = response.model_dump()

        # Create PDF attachment
        pdf = await create_pdf(response["attachment_html"])

        logger.info(f"Response from model: {response}")

        return {
            "attachments": [pdf],
            "email": response["body_html"],
            "subject": response["subject"],
        }

    async def generate_question(self, state: FakeEmailState, config):
        """Generate a fake question email."""
        question_generator = TransportQuestionGenerator()
        question = question_generator.generate_question()

        instruction = SystemMessage(
            content="You are an assistant that generates fake emails. The emails are meant for Vectrix Logistcs NV"
        )

        prompt = HumanMessage(
            content=f"""Generate a fake question email based on the following data. Write all details in the body.\n
        {question}
        """
        )

        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_complaint(self, state: FakeEmailState, config):
        """Generate a fake complaint email."""
        complaint_generator = FakeComplaint()
        complaint = complaint_generator.generate_complaint()

        instruction = SystemMessage(
            content="You are an assistant that generates fake emails. The emails are meant for Vectrix Logistcs NV"
        )

        prompt = HumanMessage(
            content=f"""Generate a fake complaint email based on the following data. Write all details in the body.\n
        {complaint}
        """
        )
        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_price_request(self, state: FakeEmailState, config):
        """Generate a fake price request email."""
        price_request_generator = PriceRequestGenerator()
        price_request = price_request_generator.generate_price_request()

        instruction = SystemMessage(
            content="You are an assistant that generates fake price negotiation emails for transport services. The emails are meant for Vectrix Logistics NV"
        )

        prompt = HumanMessage(
            content=f"""Generate a professional price negotiation email based on the following data. 
        
        IMPORTANT:
        - Use the exact company details and signature provided
        - Write in {price_request["language"]} language
        - Include the transport route: {price_request["origin"]} to {price_request["destination"]}
        - Include the transport date: {price_request["transport_date"]}
        - Make the subject abstract but related to price inquiry (e.g., "Transport inquiry {price_request["origin"]}-{price_request["destination"]}")
        - Include the price negotiation message naturally in the email body
        - End with the complete signature block provided
        
        Price request details:
        {price_request["formatted_message"]}
        """
        )

        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_waiting_costs(self, state: FakeEmailState, config):
        """Generate a fake waiting costs dispute email."""
        waiting_costs_generator = WaitingCostsGenerator()
        waiting_costs_data = waiting_costs_generator.generate_waiting_costs_scenario()

        instruction = SystemMessage(
            content="You are an assistant that generates fake dispute emails responding to waiting cost charges from Vectrans logistics company. The emails should professionally dispute the charges while maintaining a business relationship."
        )

        prompt = HumanMessage(
            content=f"""Generate a professional dispute email based on the following waiting costs scenario.
        
        IMPORTANT:
        - Vectrans is charging waiting costs for a delivery issue
        - The customer is disputing these charges
        - Use the exact dispute message and signature provided
        - Write in {waiting_costs_data["language"]} language
        - Make the subject reference the delivery issue (e.g., "RE: Waiting costs - Delivery {waiting_costs_data["scenario"]["delivery_date"]} {waiting_costs_data["scenario"]["delivery_city"]}")
        - Include the reference numbers in the email
        - Maintain a professional but firm tone
        
        Waiting costs scenario:
        - Delivery location: {waiting_costs_data["scenario"]["delivery_city"]} - {waiting_costs_data["scenario"]["destination_company"]}
        - Delivery date: {waiting_costs_data["scenario"]["delivery_date"]}
        - Order reference: {waiting_costs_data["scenario"]["order_ref"]}
        - Delivery reference: {waiting_costs_data["scenario"]["delivery_ref"]}
        - Tracking: {waiting_costs_data["scenario"]["tracking_ref"]}
        - Issue: Driver could not unload because {waiting_costs_data["scenario"]["waiting_reason"]}
        - Waiting time: {waiting_costs_data["scenario"]["waiting_hours"]} hours
        - Charged amount: {waiting_costs_data["scenario"]["total_cost"]}€
        
        Dispute response:
        {waiting_costs_data["formatted_message"]}
        """
        )

        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_update_order(self, state: FakeEmailState, config):
        """Generate a fake update order question email."""
        update_order_generator = UpdateOrderGenerator()
        update_data = update_order_generator.generate_update_order_question()

        instruction = SystemMessage(
            content="You are an assistant that generates fake update request emails about existing transport orders. The emails are meant for Vectrans NV"
        )

        prompt = HumanMessage(
            content=f"""Generate a brief professional email asking for an update about a transport order.
        
        IMPORTANT:
        - Keep the email very brief and direct
        - Use the exact greeting, question, and signature provided
        - Write in {update_data["language"]} language
        - Make the subject reference the order (e.g., "Order {update_data["order_ref"]} - Update request" or "Transport {update_data["tracking_ref"]} - Information needed")
        - The body should contain only the greeting, question, and signature
        - Do NOT add extra explanations or context
        
        Order references:
        - Order: {update_data["order_ref"]}
        - Tracking: {update_data["tracking_ref"]}
        
        Email content:
        {update_data["formatted_message"]}
        """
        )

        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_random(self, state: FakeEmailState, config):
        """Generate a random promotional email."""
        promo_generator = RandomPromotionalGenerator()
        promo_data = promo_generator.generate_promotional_email()

        instruction = SystemMessage(
            content="You are an assistant that generates fake promotional emails for logistics and transport services. The emails are meant for Vectrans NV to promote their services."
        )

        prompt = HumanMessage(
            content=f"""Generate a professional promotional email based on the following content.
        
        IMPORTANT:
        - Create an engaging promotional email in {promo_data["language"]} language
        - Use the promotional title as inspiration for the subject line
        - Include the promotional content, benefit, and call-to-action
        - Add the validity period prominently
        - Use professional but engaging marketing language
        - End with the complete signature provided
        - Make it look like a real promotional email from a logistics company
        
        Promotional content:
        - Title: {promo_data["promo_title"]}
        - Content: {promo_data["promo_content"]}
        - Key benefit: {promo_data["promo_benefit"]}
        - Call to action: {promo_data["promo_cta"]}
        - Validity: {promo_data["validity"]}
        
        Sender:
        {promo_data["signature"]}
        """
        )

        messages = [instruction, prompt]
        llm_with_tools = self.llm.with_structured_output(Email)
        response = await llm_with_tools.ainvoke(messages)
        response = response.model_dump()

        return {"email": response["body_html"], "subject": response["subject"]}

    async def generate_order(self, state: FakeEmailState, config):
        """Generate a fake transport order email."""
        transport_order_generator = TransportOrderGenerator()
        transport_order = transport_order_generator.generate().model_dump()

        logger.info(f"Generated transport order: {transport_order}")

        # Randomly select an order template (1-6)
        # order_number = random.randint(1, 6)
        order_number = 6
        logger.info(f"Selected order template: order_{order_number}")

        # Read HTML templates
        email_html = (
            resources.files("phantommail.examples")
            .joinpath(f"order_{order_number}_email.html")
            .read_text()
        )

        # Check if PDF template exists for this order
        if order_number in [1, 6]:  # Order 1 and 6 don't have a PDF template
            # Order 1 doesn't have a PDF template
            pdf_html = "no attachment"
        else:
            pdf_html = (
                resources.files("phantommail.examples")
                .joinpath(f"order_{order_number}_pdf.html")
                .read_text()
            )

        # Format transport details for use in prompts
        if order_number != 6:
            transport_details = f"""
            ## Sender details:
            - Company name: {transport_order["client"]["company"]}
            - Contact person: {transport_order["client"]["sender_name"]}
            - VAT number: {transport_order["client"]["vat_number"]}
            - Address: {transport_order["client"]["address"]}
            - City: {transport_order["client"]["city"]}
            - Postal code: {transport_order["client"]["postal_code"]}
            - Country: {transport_order["client"]["country"]}
            - Email: {transport_order["client"]["email"]}
            - Phone: {transport_order["client"]["phone"]}

            ## Goods details:
            - Description: {transport_order["goods"]}

            ## Transport dates:
            - Loading date: {transport_order["loading_date"]}
            - Unloading date: {transport_order["unloading_date"]}

            ## Pickup address:
            - Company: {transport_order["pickup_address"]["company"]}
            - Address: {transport_order["pickup_address"]["address"]}
            - Country: {transport_order["pickup_address"]["country"]}

            ## Delivery address:
            - Company: {transport_order["delivery_address"]["company"]}
            - Address: {transport_order["delivery_address"]["address"]}
            - Country: {transport_order["delivery_address"]["country"]}

            ## Intermediate Loading stops: {len(transport_order["intermediate_loading_stops"])}
            {chr(10).join([f"        - {stop['company']}, {stop['address']}, {stop['country']}" for stop in transport_order["intermediate_loading_stops"]])}

            ## Intermediate Unloading stops: {len(transport_order["intermediate_unloading_stops"])}
            {chr(10).join([f"        - {stop['company']}, {stop['address']}, {stop['country']}" for stop in transport_order["intermediate_unloading_stops"]])}
            """

        else:
            transport_details = f"""
            ## Client details (for the email signature):
            - Company name: {transport_order["client"]["company"]}
            - Contact person: {transport_order["client"]["sender_name"]}
            - VAT number: {transport_order["client"]["vat_number"]}
            - Phone: {transport_order["client"]["phone"]}
            """

        if pdf_html == "no attachment":
            prompt = f"""Generate a fake transport order email based on the following data. 
        
        IMPORTANT: Replace ALL references in the HTML template with the actual data provided below:
        - Replace all company names, addresses, contact details with the sender's information
        - Replace order numbers, dates, and transport details with realistic values
        - Replace any placeholder text with appropriate content based on the transport order
        - Ensure the email appears to come from the sender company listed below
        - If no pickup, delivery or stops information is provided, DO NOT INCLUDE it in the email!

        The transport is send to the following logistics company:
        Vectrans NV
        Kipdorpbrug 1
        2000 Antwerpen
        VAT: BE 1234.567.89


        Transport details:
        {transport_details}

        Create an email body in the following style:
        <body_html>
        {email_html}
        </body_html>

        <attachment_html>
        no attachment
        </attachment_html>
        """
        else:
            prompt = f"""Generate a fake transport order email based on the following data.
        
        IMPORTANT: Replace ALL references in BOTH the email HTML and attachment HTML templates with the actual data:
        - Replace all company names, addresses, contact details with the sender's information
        - Replace order numbers, dates, and transport details with realistic values
        - Replace any placeholder text with appropriate content based on the transport order
        - Ensure both the email and PDF attachment appear to come from the sender company
        - Make sure the attachment contains detailed transport information matching the email
        
        Transport details:
        {transport_details}

        Create an email body and attachment in the following style:
        <body_html>
        {email_html}
        </body_html>

        <attachment_html>
        {pdf_html}
        </attachment_html>
        """

        llm_with_tools = self.llm.with_structured_output(Email)

        response = await llm_with_tools.ainvoke(
            [
                HumanMessage(content=prompt),
            ]
        )

        response = response.model_dump()

        # Check if we need to create a PDF attachment based on order number
        if order_number not in [1, 6]:  # Only orders 2-5 have PDF templates
            pdf = await create_pdf(response["attachment_html"])
            attachments = [pdf]
        else:
            attachments = []

        logger.info(f"Response from model: {response}")

        return {
            "attachments": attachments,
            "email": response["body_html"],
            "subject": response["subject"],
        }

    async def send_email(self, state: FakeEmailState, config):
        """Send an email."""
        email = FullEmail(
            sender=config["configurable"].get("sender"),
            to=state["recipients"],
            attachments=state.get("attachments", []),
            body_html=state["email"],
            subject=state["subject"],
        )

        send(email)

        return {"messages": state["messages"]}
