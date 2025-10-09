from lib.string_utils import only_digits


def format_cpf(cpf: str):
    o = only_digits(cpf)
    return f'{o[0:3]}.{o[3:6]}.{o[6:9]}-{o[9:]}'


def format_process_number(process_number: str):
    o = only_digits(process_number)
    return f'{o[0:7]}-{o[7:9]}.{o[9:13]}.{o[13:14]}.{o[14:16]}.{o[16:]}'
