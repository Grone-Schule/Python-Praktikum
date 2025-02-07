import numbers
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from collections import namedtuple
import itertools

class TimeZone:
    def __init__(self, name: str, offset_hours: int, offset_minutes: int):
        if name is None or len(str(name).strip()) == 0:
            raise ValueError('Timezone name cannot be empty.')
        self._name = str(name).strip()
        if not isinstance(offset_hours, numbers.Integral):
            raise ValueError('Houer offset must be an integer.')
        if not isinstance(offset_minutes, numbers.Integral):
            raise ValueError('Minute offset must be an integer.')
        if offset_minutes > 59 or offset_minutes < -59:
            raise ValueError('Minutes offset must be between -59 and 59 (inclusiv).')
        offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        if offset < timedelta(hours=-12, minutes=0) or offset > timedelta(hours=14, minutes=0):
            raise ValueError('Offset must be between -12:00 and +14:00.')
        self._offset_hours = offset_hours
        self._offset_minutes = offset_minutes
        self._offset = offset


    @property
    def name(self):
        return self._name

    @property
    def offset(self):
        return self._offset

    def __eq__(self, other):
        return (isinstance(other, TimeZone) and
                self.name == other.name and
                self._offset_hours == other._offset_hours and
                self._offset_minutes == other._offset_minutes)

    def __repr__(self):
        return (f'TimeZone(name="{self.name}", '
                f'offset-houers={self._offset_minutes}'
                f'offset_minutes={self._offset_minutes})')

    #def __str__(self):
       # return f"{self._name} (UTC{'+' if self._offset.total_seconds() >= 0 else '-'}{abs(self._offset)})"



class BankAccount():
    _interest_rate = 0.5  # Class-level property for interest rate
    transaction_id = itertools.count(100)
    def __init__(self, account_number, first_name, last_name, time_zone=None, balance=0.00):
        if balance < 0:
            raise ValueError("Balance cannot be negative!")
        self._account_number = account_number
        self.first_name = first_name
        self.last_name = last_name
        self.time_zone = time_zone
        self._balance = Decimal(str(balance))


    def make_transaction(self):
        new_trans_id = next(BankAccount.transaction_id)
        return new_trans_id

    @property
    def account_number(self):
        return self._account_number

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self.validate_and_set_name('_first_name', value, 'First Name')

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self.validate_and_set_name('_last_name', value, 'Last Name')


    def validate_and_set_name(self, attr_name, value, field_titel):
        if value is None or len(str(value).strip()) == 0:
            raise ValueError(f'{field_titel} cannot be empty.')
        setattr(self, attr_name, value)

    @property
    def timezone(self):
        return self._time_zone

    @timezone.setter
    def timezone(self, value):
        if not isinstance(value, TimeZone):
            raise ValueError('Time Zone must be a valid TimeZone object.')
        self._time_zone = value

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def balance(self):
        if self._balance < 0:
            raise ValueError('Balance must be pozitive')
        else:

            return self._balance

    @classmethod
    def get_interest_rate(cls):
        #cls._interest_rate = Decimal(str(cls._interest_rate))
        return cls._interest_rate

    @classmethod
    def set_interst_rate(cls, value):
       # if not isinstance(value, numbers.Real):
            #raise ValueError('Interest rate must be a real number.')
        if value < 0:
            raise ValueError('Interest rate cannot be negative.')
        cls._interest_rate = Decimal(value)


    def confirmation_number(self, transaction_code: str):
        utc_time = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        return f"{transaction_code}-{self._account_number}-{utc_time}-{next(BankAccount.transaction_id)}"


    def deposit(self, amount: Decimal):
        #if not isinstance(amount, numbers.Real):
            #raise ValueError('Deposit value must be a real number.')
        if amount < 0:
            raise ValueError("Deposit amount must be positive!")
        else:
            self._balance += amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        return self.confirmation_number('D')

    def withdraw(self, amount: Decimal):
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive!")
        if self._balance - amount < 0:
            return self.confirmation_number('X')  # Declined transaction
        else:
            self._balance -= amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        return self.confirmation_number('W')

    def pay_interest(self):
        interest = (self._balance * self._interest_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
        self._balance += interest
        return self.confirmation_number('I')

    def result(self, confirmation_number: str):
        parts = confirmation_number.split('-')
        if len(parts) != 4:
            raise ValueError("Invalid confirmation number format")
        transaction_code, account_number, time_utc, transaction_id = parts
        time_utc = datetime.strptime(time_utc, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
        local_time = time_utc + self.time_zone.offset
        Result = namedtuple('Result',
                            ['account_number',
                                       'transaction_code',
                                       'transaction_id',
                                       'time',
                                       'time_utc'])
        result = Result(
            account_number=account_number,
            transaction_code=transaction_code,
            transaction_id=int(transaction_id),
            time=local_time.strftime('%Y-%m-%d %H:%M:%S (%Z)'),
            time_utc=time_utc.strftime('%Y-%m-%dT%H:%M:%S')
        )
        return result


# Example Usage
time_zone = TimeZone("MST", -7, 0)
account = BankAccount("140568", "John", "Doe", time_zone, Decimal("100.00"))

print(account.full_name)  # John Doe
print(account.balance)    # 100.00
print(account.deposit(Decimal("150.02")))  # Generates confirmation number
print(account.balance)
print(account.withdraw(Decimal("0.02")))  # Generates confirmation number
print(account.balance)
BankAccount.set_interst_rate(Decimal('0.01'))
print((account.get_interest_rate()))
print(account.pay_interest())
print(account.balance)
print(account.withdraw(Decimal('1000')))

import unittest

def run_test(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account_number = 'A100'
        self.first_name = 'FIRST'
        self.last_name = 'LAST'
        self.tz = TimeZone('TZ', 1, 30)
        self.balance = 100.00
        self.withdrawal_amount = 20

    def create_account(self):
        return BankAccount(self.account_number, self.first_name, self.last_name, self.tz, self.balance)

    def test_create_timezone(self):
        tz = TimeZone('ABC', -1, -30)
        self.assertEqual('ABC', tz.name)
        self.assertEqual(timedelta(hours=-1, minutes=-30), tz.offset)

    def test_timezones_equal(self):
        tz1 = TimeZone('ABC', -1, -30)
        tz2 = TimeZone('ABC', -1, -30)
        self.assertEqual(tz1, tz2)

    def test_timezones_not_equal(self):
        tz = TimeZone('ABC', -1, -30)

        test_timezones = (
            TimeZone('DEF', -1, -30),
            TimeZone('ABC', -1, 0),
            TimeZone('ABC', 1, -30)
        )
        for i, test_tz in enumerate(test_timezones):
            with self.subTest(test_name=f'Test #{i}'):
                self.assertNotEqual(tz, test_tz)

    def test_create_account(self):
        a = self.create_account()

        self.assertEqual(self.account_number, a.account_number)
        self.assertEqual(self.first_name, a.first_name)
        self.assertEqual(self.last_name, a.last_name)
        self.assertEqual(self.first_name + " " + self.last_name, a.full_name)
        self.assertEqual(self.tz, a.time_zone)
        self.assertEqual(self.balance, a.balance)

    def test_create_account_blank_first_name(self):
        self.first_name = ''

        with self.assertRaises(ValueError):
            a = self.create_account()

    def test_create_account_negative_balance(self):
        self.balance = -100.00

        with self.assertRaises(ValueError):
            a = self.create_account()

    def test_account_withdraw_ok(self):
        self.withdrawal_amount = 20

        a = self.create_account()
        conf_code = a.withdraw(Decimal(self.withdrawal_amount))
        self.assertTrue(conf_code.startswith('W-'))
        self.assertEqual(self.balance - self.withdrawal_amount, a.balance)

    def test_account_withdraw_overdraw(self):
        self.withdrawal_amount = 200

        a = self.create_account()
        conf_code = a.withdraw(Decimal(self.withdrawal_amount))
        self.assertTrue(conf_code.startswith('X-'))
        self.assertEqual(self.balance, a.balance)

run_test(TestAccount)
