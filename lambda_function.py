from html.parser import HTMLParser

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

from utils import *

quantity_key = "QUANTITY"
sides_key = "SIDES"
dice_key = "DICE"

number_slot = "number"
roll_slot = "rolloption"

skill_name = "Dice Roller"
quantity_help_text = ("Please tell me how many dice you would like to roll. "
                      "You can give me a number from one to ten.")
sides_help_text = ("Please give me a number from 2 to 20. "
                   "For example, the average dice used for board games has 6 sides.")
roll_help_text = "Ready for me to roll? You can say yes or roll to start or no to wait."

sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    print("LaunchRequest")
    response_builder = handler_input.response_builder
    speech = "Welcome to dice roller."

    response_builder.speak(speech + " " + quantity_help_text).ask(quantity_help_text)
    return response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    response_builder = handler_input.response_builder
    response_builder.speak(quantity_help_text).ask(quantity_help_text)
    return response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input:
    is_request_type("SessionEndedRequest")(handler_input) or
    is_intent_name("AMAZON.CancelIntent")(handler_input) or
    is_intent_name("AMAZON.NavigateHomeIntent")(handler_input) or
    is_intent_name("AMAZON.StopIntent")(handler_input))
def end_intent_handler(handler_input):
    handler_input.response_builder.speak("Thank you for using dice roller. Goodbye!")
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("NumberIntent"))
def number_handler(handler_input):
    print("NumberIntent")
    slots = handler_input.request_envelope.request.intent.slots
    session_attributes = handler_input.attributes_manager.session_attributes

    if quantity_key not in session_attributes:
        results = dice_quantity_handler(slots, session_attributes)
    else:
        results = dice_side_handler(slots, session_attributes)

    handler_input.response_builder.speak(results.speech).ask(results.reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    speech = f"The {skill_name} skill can't help you with that."
    handler_input.response_builder.speak(speech).ask("")
    return handler_input.response_builder.response


def convert_speech_to_text(ssml_speech):
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


@sb.global_response_interceptor()
def add_card(_, response):
    response.card = SimpleCard(
        title=skill_name,
        content=convert_speech_to_text(response.output_speech.ssml) if response.output_speech is not None else ""
    )


@sb.global_response_interceptor()
def log_response(_, response):
    print(f"Alexa Response: {response}\n")


@sb.global_request_interceptor()
def log_request(handler_input):
    print(f"Alexa Request: {handler_input.request_envelope.request}\n")


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    print(f"Encountered following exception: {exception}")

    speech = "Sorry, I had a problem with the last request. Please try again."
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


class SSMLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.full_str_list = []
        self.strict = False

    def get_data(self):
        return ''.join(self.full_str_list)

    def handle_data(self, d):
        self.full_str_list.append(d)

    def error(self, message):
        print("error converting to speech: " + message)


class LambdaResults:

    def __init__(self, speech, reprompt=""):
        self.speech = speech
        self.reprompt = reprompt


def dice_quantity_handler(slots: dict, session_attributes: dict) -> LambdaResults:
    if number_slot in slots:
        dice_quantity = slots[number_slot].value
        if not validate_quantity(dice_quantity):
            return LambdaResults(
                speech=f"I don't know how to roll {quantity_to_speech(dice_quantity)}.",
                reprompt=quantity_help_text
            )
        else:
            session_attributes[quantity_key] = int(dice_quantity)
            return LambdaResults(
                speech=(f"How many sides would you like the {quantity_to_speech(dice_quantity)} to have? "
                        f"You can give me a number from 2 to 20."),
                reprompt=sides_help_text
            )
    else:
        return LambdaResults(
            speech="I'm not sure how many dice you would like to roll.",
            reprompt=quantity_help_text
        )


def dice_side_handler(slots: dict, session_attributes: dict) -> LambdaResults:
    if number_slot in slots:
        num_sides = slots[number_slot].value
        if not validate_sides(num_sides):
            return LambdaResults(
                speech=f"I only know how to roll dice with at least 2 but not more than 20 sides.",
                reprompt=sides_help_text
            )
        else:
            session_attributes[sides_key] = int(num_sides)
            return LambdaResults(
                speech=(f"OK, I will roll {quantity_to_speech(session_attributes[quantity_key])} with {num_sides} "
                        "sides. Ready for me to roll?"),
                reprompt=roll_help_text
            )
    else:
        return LambdaResults(speech=roll_help_text, reprompt=roll_help_text)


# Handler to be provided in lambda console.
lambda_handler = sb.lambda_handler()
