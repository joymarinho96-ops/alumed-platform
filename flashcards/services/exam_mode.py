def get_exam_mode(days_until_exam: int) -> str:
    """
    Retorna o modo de estudo baseado em quantos dias restam até o exame.
    - emergency (≤ 2 dias)
    - intensive (≤ 7 dias)
    - reinforcement (≤ 14 dias)
    - normal (> 14 dias)
    """
    if days_until_exam <= 2:
        return "emergency"

    if days_until_exam <= 7:
        return "intensive"

    if days_until_exam <= 14:
        return "reinforcement"

    return "normal"
