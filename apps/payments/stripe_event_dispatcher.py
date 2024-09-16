import importlib
import logging


class StripeEventDispatcher:
    def __init__(
        self, event_type: str, event_data: dict, connected_account: str = None
    ):
        self.event_type = event_type
        self.event_data = event_data
        self.connected_account = connected_account

    def dispatch(self):
        event_handler = self.get_handler()
        if event_handler:
            handler = event_handler(self.event_data)
            handler.handle()
        else:
            logging.error(f"Unable to dispatch event for type: {self.event_type}")

    def get_handler(self):
        event_group = self.event_type.split(".")[0]
        account_type = "connect" if self.connected_account else "platform"
        module_path = f"apps.payments.stripe_handlers.{account_type}_events.{event_group}_handlers"

        try:
            handler_module = importlib.import_module(module_path)
            handler_name = self._to_camel_case(self.event_type) + "Handler"
            handler_class = getattr(handler_module, handler_name, None)

            if handler_class:
                return handler_class
            else:
                logging.error(
                    f"Handler class '{handler_name}' not found in module '{module_path}' for event type: {self.event_type}"
                )
                return None

        except ModuleNotFoundError:
            logging.error(
                f"Module '{module_path}' not found for event group: {event_group} in {account_type}"
            )
            return None
        except AttributeError:
            logging.error(
                f"Failed to find handler class '{handler_name}' in module '{module_path}' for event type: {self.event_type}"
            )
            return None

    @staticmethod
    def _to_camel_case(event_type: str) -> str:
        components = event_type.replace("_", " ").split(".")
        camel_case_string = "".join(x.title().replace(" ", "") for x in components)
        return camel_case_string
