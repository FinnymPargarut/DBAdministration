import re
from models import Client, Tour, Booking, Payment


class ValidateRegEx:
    @staticmethod
    def is_integer(text):
        integer_pattern = re.compile(r'^\d+$')
        return bool(integer_pattern.match(text))

    @staticmethod
    def is_date(text):
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        return bool(date_pattern.match(text))

    @staticmethod
    def is_phone_number(text):
        phone_pattern = re.compile(r'^\+7\d{10}$')
        return bool(phone_pattern.match(text))

    @staticmethod
    def is_status(text):
        if text in ('pending', 'confirmed', 'cancelled', 'completed'):
            return True
        return False

    @staticmethod
    def is_invalid(text, type):
        if type == "INTEGER":
            return not ValidateRegEx.is_integer(text)
        elif type == "DATE":
            return not ValidateRegEx.is_date(text)
        elif type == "PHONE":
            return not ValidateRegEx.is_phone_number(text)
        elif type == "STATUS":
            return not ValidateRegEx.is_status(text)
        elif type == "ID":
            return True
        return False

    @staticmethod
    def is_where(text):
        where_pattern = re.compile(r'^[><=].+$')
        return bool(where_pattern.match(text))

    @staticmethod
    def is_attribute(text, attributes):
        lst = [s.strip() for s in text.split(',')]
        return all(attr in attributes for attr in lst), len(lst)

    @staticmethod
    def is_direction(text):
        lst = [s.strip() for s in text.split(',')]
        return all(direct in ["ASC", "DESC"] for direct in lst), len(lst)

    @staticmethod
    def validate_filter_data(condition, attribute, attributes, direction):
        check1 = ValidateRegEx.is_where(condition)
        check2, len1 = ValidateRegEx.is_attribute(attribute, attributes)
        check3, len2 = ValidateRegEx.is_direction(direction)
        return check1 and check2 and check3 and len1 == len2


class BaseController:
    def __init__(self, table_name, repo):
        self.table_name = table_name
        self.repo = repo
        self.validation = ValidateRegEx
        self.attr_types = self.repo.get_attr_types(self.table_name)
        self.attr_names = self.repo.get_attr_names(self.table_name)

    def get_attr_names(self):
        return self.attr_names

    def get_attr_types(self):
        return self.attr_types

    def get_columns_count(self):
        return len(self.attr_names)

    def validate_filter(self, condition, attribute, direction):
        return self.validation.validate_filter_data(condition, attribute, self.get_attr_names(), direction)


class ClientController(BaseController):
    def __init__(self, client_repo):
        super().__init__("clients", client_repo)

    def get_all_clients(self):
        return self.repo.get_all()

    def get_client_by_id(self, client_id):
        return self.repo.get_by_id(client_id)

    def add_client(self, client):
        self.repo.add(client)

    def update_client(self, client):
        self.repo.update(client)

    def delete_client(self, client_id):
        self.repo.delete(client_id)

    def is_invalid_type(self, text, column, ids=False):
        current_type = self.attr_types[column]
        if self.attr_names[column] == "phone":
            current_type = "PHONE"
        elif "id" in self.attr_names[column] and ids:
            current_type = "ID"

        res = self.validation.is_invalid(text, current_type)
        return res

    def filter_clients(self, order_by=None, order_direction="ASC", **kwargs):
        if not order_by:
            order_by = self.get_attr_names()[0]
        if not kwargs:
            return self.repo.filter_by(self.table_name, Client, order_by, order_direction)
        return self.repo.filter_by(self.table_name, Client, order_by, order_direction, **kwargs)


class TourController(BaseController):
    def __init__(self, tour_repo):
        super().__init__("tours", tour_repo)

    def get_all_tours(self):
        return self.repo.get_all()

    def get_tour_by_id(self, tour_id):
        return self.repo.get_by_id(tour_id)

    def add_tour(self, tour):
        self.repo.add(tour)

    def update_tour(self, tour):
        self.repo.update(tour)

    def delete_tour(self, tour_id):
        self.repo.delete(tour_id)

    def is_invalid_type(self, text, column, ids=False):
        current_type = self.attr_types[column]
        if "id" in self.attr_names[column] and ids:
            current_type = "ID"

        res = self.validation.is_invalid(text, current_type)
        return res

    def filter_tours(self, order_by=None, order_direction="ASC", **kwargs):
        if not order_by:
            order_by = self.get_attr_names()[0]
        if not kwargs:
            return self.repo.filter_by(self.table_name, Tour, order_by, order_direction)
        return self.repo.filter_by(self.table_name, Tour, order_by, order_direction, **kwargs)


class BookingController(BaseController):
    def __init__(self, booking_repo):
        super().__init__("bookings", booking_repo)

    def get_all_bookings(self):
        return self.repo.get_all()

    def get_booking_by_id(self, booking_id):
        return self.repo.get_by_id(booking_id)

    def total_price_counting(self, booking):
        return self.repo.get_price_by_tour_id(booking.tour_id) * int(booking.people_number)

    def add_booking(self, booking):
        self.repo.add(booking)

    def update_booking(self, booking):
        self.repo.update(booking)

    def delete_booking(self, booking_id):
        self.repo.delete(booking_id)

    def is_invalid_type(self, text, column, ids=False):
        current_type = self.attr_types[column]
        if self.attr_names[column] == "status":
            current_type = "STATUS"
        elif "id" in self.attr_names[column] and ids:
            current_type = "ID"
        elif self.attr_names[column] == "client_id" and not self.validation.is_invalid(text, current_type):
            return int(text) not in self.repo.get_clients_id_list()
        elif self.attr_names[column] == "tour_id" and not self.validation.is_invalid(text, current_type):
            return int(text) not in self.repo.get_tours_id_list()

        res = self.validation.is_invalid(text, current_type)
        return res

    def filter_bookings(self, order_by=None, order_direction="ASC", **kwargs):
        if not order_by:
            order_by = self.get_attr_names()[0]
        if not kwargs:
            return self.repo.filter_by(self.table_name, Booking, order_by, order_direction)
        return self.repo.filter_by(self.table_name, Booking, order_by, order_direction, **kwargs)


class PaymentController(BaseController):
    def __init__(self, payment_repo):
        super().__init__("payments", payment_repo)

    def get_all_payments(self):
        return self.repo.get_all()

    def get_payment_by_id(self, payment_id):
        return self.repo.get_by_id(payment_id)

    def add_payment(self, payment):
        self.repo.add(payment)

    def update_payment(self, payment):
        self.repo.update(payment)

    def delete_payment(self, payment_id):
        self.repo.delete(payment_id)

    def is_invalid_type(self, text, column, ids=False):
        current_type = self.attr_types[column]
        if "id" in self.attr_names[column] and ids:
            current_type = "ID"
        elif self.attr_names[column] == "booking_id" and not self.validation.is_invalid(text, current_type):
            return int(text) not in self.repo.get_bookings_id_list()

        res = self.validation.is_invalid(text, current_type)
        return res

    def filter_payments(self, order_by=None, order_direction="ASC", **kwargs):
        if not order_by:
            order_by = self.get_attr_names()[0]
        if not kwargs:
            return self.repo.filter_by(self.table_name, Payment, order_by, order_direction)
        return self.repo.filter_by(self.table_name, Payment, order_by, order_direction, **kwargs)
