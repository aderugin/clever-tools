Cart configuration for Robokassa
================================

### settings.py

MRCHLOGIN = 'demo'
MRCHPASS1 = 'password_1'
MRCHPASS2 = 'password_2'

### cart/models.py

Class Order():
    price = price_field

    def set_status_paid(self):
        // changeing status & save

