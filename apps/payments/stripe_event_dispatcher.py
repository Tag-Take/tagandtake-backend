import importlib
import logging


class StripeEventDispatcher:
    def __init__(
        self, event_type: str, event_data: dict[any], connected_account: str = None
    ):
        self.event_type = event_type
        self.event_data = event_data
        self.connected_account = connected_account

    def dispatch(self):
        event_group = self.event_type.split(".")[0]
        account_type = (
            "connect" if self.connected_account else "platform"
        )

        module_path = f"apps.payments.stripe_handlers.{account_type}_events.{event_group}_handlers"

        try:
            handler_module = importlib.import_module(module_path)
            handler_function_name = f"handle_{self.event_type.replace('.', '_')}"
            handler_function = getattr(handler_module, handler_function_name, None)

            if handler_function:
                handler_function(self.event_data)
            else:
                logging.error(
                    f"Handler function '{handler_function_name}' not found in module '{module_path}' for event type: {self.event_type}"
                )

        except ModuleNotFoundError as e:
            logging.error(
                f"Module '{module_path}' not found for event group: {event_group} in {account_type}"
            )
        except AttributeError as e:
            logging.error(
                f"Failed to find handler function '{handler_function_name}' in module '{module_path}' for event type: {self.event_type}"
            )
