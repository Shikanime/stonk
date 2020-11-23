import click
import decimal
import os
from typing import Dict, Union, cast
from datetime import datetime
from binance.client import Client
from functools import reduce

client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))


@click.group()
def cli():
    pass


@cli.group()
def order():
    pass


@order.command()
@click.option('--symbol',
              type=str,
              required=True,
              help='Symbol')
@click.option('--price',
              type=decimal.Decimal,
              required=True,
              help='Entry price')
@click.option('--target',
              type=float,
              required=True,
              help='Target percent price')
@click.option('--ratio',
              type=decimal.Decimal,
              required=True,
              help='Ratio')
@click.option('--quantity',
              type=decimal.Decimal,
              required=True,
              help='Quantity')
@click.option('--time-in-force',
              type=str,
              help='Limit order time in force')
@click.option('--auto-approve',
              default=False,
              type=decimal.Decimal,
              help='Skip confirmation step')
def sell(**kwargs: Dict[str, Union[str, decimal.Decimal, float]]):
    target = cast(float, kwargs.pop('target'))
    price = cast(decimal.Decimal, kwargs.pop('price'))
    ratio = cast(decimal.Decimal, kwargs.pop('ratio'))

    gain = (price / 100 * (decimal.Decimal(target) * 100))
    loss = gain / ratio
    target = (price + gain).quantize(decimal.Decimal('1.00000'))
    limit = (price - loss).quantize(decimal.Decimal('1.00000'))
    stop = limit - decimal.Decimal('0.00001')

    plan = "\n".join([
        "Target: {}".format(target),
        "Stop:   {}".format(stop),
        "Limit:  {}".format(limit)
    ])
    msg = "\n\n".join([
        plan,
        'Proceed?'
    ])

    def handle(**kwargs):
        if not cast(bool, kwargs.pop('auto_approve')) and not click.confirm(msg):
            return click.style("Order canceled", fg="red")

        now = datetime.now()

        history = client.create_test_order(**normalize_options({
            'price': price,
            'side': Client.SIDE_SELL,
            'type': Client.ORDER_TYPE_STOP_LOSS_LIMIT,
            'stop_price': stop,
            'new_order_resp_type': Client.ORDER_RESP_TYPE_RESULT,
            'timestamp': now.timestamp(),
            ** kwargs
        }))

        delta = datetime.fromtimestamp(history["transactTime"]) - now
        delta_ms = delta.microseconds / 1000
        delta_ms_str = "{}ms".format(delta_ms)

        return click.style("Order confirmed in: {}".format(delta_ms_str),
                           fg="green")

    click.echo("\n" + handle(**kwargs))


@order.command()
@click.option('--symbol',
              type=str,
              required=True,
              help='Symbol')
@click.option('--price',
              type=decimal.Decimal,
              required=True,
              help='Entry price')
@click.option('--target',
              type=float,
              required=True,
              help='Target percent price')
@click.option('--ratio',
              type=decimal.Decimal,
              required=True,
              help='Ratio')
@click.option('--quantity',
              type=decimal.Decimal,
              required=True,
              help='Quantity')
@click.option('--auto-approve',
              default=False,
              type=decimal.Decimal,
              help='Skip confirmation step')
def buy(**kwargs: Dict[str, Union[str, decimal.Decimal, float]]):
    target = cast(float, kwargs.pop('target'))
    price = cast(decimal.Decimal, kwargs.pop('price'))
    ratio = cast(decimal.Decimal, kwargs.pop('ratio'))

    gain = (price / 100 * (decimal.Decimal(target) * 100))
    loss = gain / ratio
    target = (price + gain).quantize(decimal.Decimal('1.00000'))
    limit = (price - loss).quantize(decimal.Decimal('1.00000'))
    stop = limit - decimal.Decimal('0.00001')

    plan = "\n".join([
        "Target: {}".format(target),
        "Stop:   {}".format(stop),
        "Limit:  {}".format(limit)
    ])
    msg = "\n\n".join([
        plan,
        'Proceed?'
    ])

    def handle(**kwargs):
        if not cast(bool, kwargs.pop('auto_approve')) and not click.confirm(msg):
            return click.style("Order canceled", fg="red")

        now = datetime.now()

        client.create_test_order(**normalize_options({
            'price': price,
            'side': Client.SIDE_BUY,
            'type': Client.ORDER_TYPE_LIMIT,
            'time_in_force': stop,
            'new_order_resp_type': Client.ORDER_RESP_TYPE_FULL,
            **kwargs
        }))

        delta = datetime.now() - now
        delta_ms = delta.microseconds / 1000
        delta_ms_str = "{}ms".format(delta_ms)

        return click.style("Order confirmed in: {}".format(delta_ms_str),
                           fg="green")

    click.echo("\n" + handle(**kwargs))


def normalize_options(opts):
    def normalize_key(k):
        words = k.split('_')
        return words[0] + ''.join(x.title() for x in words[1:])

    def normalize_value(v):
        if isinstance(v, decimal.Decimal):
            return str(v)
        return v

    def normalize_kv(acc, x):
        if x[1] is None:
            return acc
        return {normalize_key(x[0]): normalize_value(x[1]), **acc}

    return reduce(normalize_kv, opts.items(), {})


if __name__ == "__main__":
    cli()
