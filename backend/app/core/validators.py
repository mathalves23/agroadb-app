"""
Validação completa de CPF e CNPJ — algoritmo de dígitos verificadores
"""
import re
from typing import Optional


def limpar_documento(doc: str) -> str:
    """Remove formatação de um documento (pontos, traços, barras)."""
    return re.sub(r'\D', '', doc.strip())


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo oficial dos dígitos verificadores.

    Args:
        cpf: CPF com ou sem formatação

    Returns:
        True se válido
    """
    cpf = limpar_documento(cpf)

    if len(cpf) != 11:
        return False

    # Rejeitar sequências repetidas (111.111.111-11, etc.)
    if cpf == cpf[0] * 11:
        return False

    # Calcular primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Calcular segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cpf[10]) == digito2


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo oficial dos dígitos verificadores.

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        True se válido
    """
    cnpj = limpar_documento(cnpj)

    if len(cnpj) != 14:
        return False

    # Rejeitar sequências repetidas
    if cnpj == cnpj[0] * 14:
        return False

    # Pesos para cálculo
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Primeiro dígito verificador
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Segundo dígito verificador
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return int(cnpj[13]) == digito2


def validar_documento(doc: str) -> tuple[bool, str]:
    """
    Valida CPF ou CNPJ automaticamente baseado no tamanho.

    Args:
        doc: Documento com ou sem formatação

    Returns:
        Tupla (is_valid, tipo) onde tipo é 'cpf', 'cnpj' ou 'invalido'
    """
    cleaned = limpar_documento(doc)

    if len(cleaned) == 11:
        return validar_cpf(cleaned), 'cpf'
    elif len(cleaned) == 14:
        return validar_cnpj(cleaned), 'cnpj'
    else:
        return False, 'invalido'


def formatar_cpf(cpf: str) -> str:
    """Formata CPF: 000.000.000-00"""
    cpf = limpar_documento(cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ: 00.000.000/0000-00"""
    cnpj = limpar_documento(cnpj)
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_documento(doc: str) -> str:
    """Formata CPF ou CNPJ automaticamente."""
    cleaned = limpar_documento(doc)
    if len(cleaned) == 11:
        return formatar_cpf(cleaned)
    elif len(cleaned) == 14:
        return formatar_cnpj(cleaned)
    return doc
