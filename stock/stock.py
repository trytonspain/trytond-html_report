from trytond.model import fields
from trytond.pool import PoolMeta, Pool


class ShipmentOutReturn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out.return'

    show_lots = fields.Function(fields.Boolean('Show Lots'),
        'get_show_lots')

    def get_show_lots(self, name):
        for move in self.incoming_moves:
            if getattr(move, 'lot'):
                return True
        return False


class ShipmentInReturn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in.return'

    show_lots = fields.Function(fields.Boolean('Show Lots'),
        'get_show_lots')

    def get_show_lots(self, name):
        for move in self.moves:
            if getattr(move, 'lot'):
                return True
        return False


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    sorted_lines = fields.Function(fields.One2Many('stock.move',
        'line', 'Sorted Lines'), 'get_sorted_lines')
    sorted_keys = fields.Function(fields.Char('key'), 'get_sorted_keys')
    show_lots = fields.Function(fields.Boolean('Show Lots'),
        'get_show_lots')

    def get_sorted_lines(self, name):
        lines = [x for x in self.inventory_moves or self.outgoing_moves]
        lines.sort(key=lambda k: k.sort_key, reverse=True)
        return [x.id for x in lines]

    def get_sorted_keys(self, name):
        keys = []
        for x in self.sorted_lines:
            if x.sort_key in keys:
                continue
            keys.append(x.sort_key)
        return keys

    def get_show_lots(self, name):
        for move in self.inventory_moves or self.outgoing_moves:
            if getattr(move, 'lot'):
                return True
        return False


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    sort_key = fields.Function(fields.Char('key'), 'get_sorted_key')

    def get_sorted_key(self, name):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        ShipmentIn = pool.get('stock.shipment.in')

        key = []
        if self.shipment and isinstance(self.shipment, ShipmentOut):
            if self.shipment.warehouse_storage == self.shipment.warehouse_output:
                sale = (self.origin
                        and ('sale.line' in str(self.origin))
                        and self.origin.sale or None)
            else:
                sale = (self.origin
                        and self.origin.origin
                        and ('sale.line' in str(self.origin.origin))
                        and self.origin.origin.sale or None)
            if sale and sale not in key:
                key.append(sale)

        elif self.shipment_in and isinstance(self.shipment, ShipmentIn):
            if self.origin and 'purchase.line' in str(self.origin):
                purchase = self.origin.purchase
                if purchase in key:
                    key.append(purchase)
        return key
