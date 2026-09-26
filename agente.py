"""Exemplo de agente determinístico com aprovação antes da ação."""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class Proposta:
    id: str
    acao: str
    documento: str


class CaixaDeSaidaFicticia:
    """Ferramenta local; guarda registros apenas na memória do processo."""

    def __init__(self):
        self.registros = {}

    def registrar(self, proposta):
        if proposta.id not in self.registros:
            self.registros[proposta.id] = f"Registrado para revisão: {proposta.documento}"
        return self.registros[proposta.id]


def propor_registro(documento):
    documento = documento.strip()
    if not documento or len(documento) > 100:
        raise ValueError("Informe um nome de documento com até 100 caracteres")
    identificador = sha256(f"registrar:{documento}".encode("utf-8")).hexdigest()[:12]
    return Proposta(identificador, "registrar para revisão", documento)


def executar(proposta, decisao, ferramenta):
    if decisao != "aprovar":
        return "Ação não executada: aprovação ausente ou recusada."
    return ferramenta.registrar(proposta)


def main():
    nome = input("Nome de um documento fictício: ")
    proposta = propor_registro(nome)
    print(f"Proposta {proposta.id}: {proposta.acao} '{proposta.documento}'")
    decisao = input("Digite aprovar para registrar (qualquer outra resposta cancela): ").strip().lower()
    print(executar(proposta, decisao, CaixaDeSaidaFicticia()))


if __name__ == "__main__":
    main()
