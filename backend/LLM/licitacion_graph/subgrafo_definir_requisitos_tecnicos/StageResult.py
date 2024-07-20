

class StageResult:
    def __init__(self, etapa: str, index_etapa: int, tecnologias: list[str]):
        self.etapa = etapa
        self.index_etapa = index_etapa
        self.tecnologias = tecnologias

    def __str__(self):
        return f"\n{self.etapa}: \n{self.tecnologias}"
