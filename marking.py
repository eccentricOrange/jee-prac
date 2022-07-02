import collections

def mark_numeric(answer: float, attempt: float, wrong: int, correct: int, unattempted: int = 0) -> float:
    """
    Mark a numeric question.
    """
  
    if attempt:
        if answer == attempt:
            return correct
        else:
            return wrong

    return unattempted


def mark_text(answer: str, attempt: str, wrong: int, correct: int, unattempted: int = 0) -> float:
    """
    Mark a text question.
    """
  
    if attempt:
        if answer == attempt:
            return correct
        else:
            return wrong

    return unattempted


def mark_mcq_scc(answer: str, attempt: str, wrong: int, correct: int, unattempted: int = 0) -> float:
    """
    Mark a multiple choice question with single correct choice.
    """
   
    if attempt:
        if answer == attempt:
            return correct
        else:
            return wrong

    return unattempted

def mark_mcq_mcc(answer: tuple[str], attempt: tuple[str], wrong: int, correct: dict[int, int], unattempted: int = 0) -> float:
    """
    Mark a multiple choice question with multiple correct choices.
    """
    
    if attempt:
        collections.