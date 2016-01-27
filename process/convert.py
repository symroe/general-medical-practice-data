#!/usr/bin/env python

import csv
import json

from collections import OrderedDict


HEADER = [
    'organisation_code',
    'name',
    'national_grouping',
    'high_level_health_geography',
    'address_line_1',
    'address_line_2',
    'address_line_3',
    'address_line_4',
    'address_line_5',
    'postcode',
    'open_date',
    'close_date',
    'status_code',
    'organisation_sub_type_code',
    'commissioner',
    'join_provider_purchaser_date',
    'left_provider_purchaser_date',
    'contact_telephone_number',
    'null_1',
    'null_2',
    'null_3',
    'amended_record_indicator',
    'null_4',
    'provider_purchaser',
    'null_5',
    'prescribing_setting',
    'null_6',
]


def main(argv):
    csv_rows = open_csv_file(argv[1])

    amendments = load_amendment_files(argv[2:])

    amended_rows = apply_amendments(csv_rows, amendments)

    filtered_rows = filter_rows(amended_rows)

    transformed_rows = transform_rows(filtered_rows)

    output_json(transformed_rows)


def usage():
    sys.stderr.write('Usage: {} <current.json> <amendment.json..>\n'.format(
        sys.argv[0]))


def apply_amendments(rows, amendments):
    for row in rows:
        try:
            amended_row = amendments.pop(row['organisation_code'])
            sys.stderr.write('Amend {}: {} -> {}\n'.format(
                row['organisation_code'], row, amended_row))

            yield amended_row

        except KeyError:  # no amended row for this practice
            yield row

    sys.stderr.write('{} NEW practices: {}'.format(
        len(amendments.keys()),
        ', '.join(amendments.keys())))

    for row in amendments.values():
        yield row


def write_output(rows):
    json.dump(list(rows), sys.stdout, indent=4)


def load_amendment_files(csv_filenames):
    amendments = {}

    for filename in csv_filenames:
        for row in open_csv_file(filename):
            amendments[row['organisation_code']] = row

    return amendments


def open_csv_file(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, HEADER)
        for row in reader:
            yield row


def filter_rows(csv_rows):

    def is_active_gp(row):
        return row['prescribing_setting'] == '4' and row['status_code'] == 'A'

    return filter(is_active_gp, csv_rows)


def transform_rows(rows):
    def combine_address_parts(row):
        address_part_keys = ['address_line_{}'.format(i)
                             for i in [1, 2, 3, 4, 5]]

        return ', '.join(
            filter(None, [row[key].title() for key in address_part_keys]) +
            [row['postcode']]
        )

    def transform_row(row):
        combined_address = combine_address_parts(row)

        return OrderedDict([
            ('organisation_code', row['organisation_code']),
            ('name', row['name'].title()),
            ('address', combined_address),
            ('contact_telephone_number', row['contact_telephone_number']),
        ])

    return map(transform_row, rows)


def output_json(rows):
    json.dump(
        sorted(list(rows), key=lambda row: row['organisation_code']),
        sys.stdout,
        indent=4)


if __name__ == '__main__':
    import sys
    main(sys.argv)
