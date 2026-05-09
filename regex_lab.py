"""Regular Expression"""
from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """
    Abstract base class for finite state machine states.
    """
    @abstractmethod
    def __init__(self) -> None:
        """
        Initializes a base state with an empty list of next states.
        """
        self.next_states: list[State] = []
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        """
        Finds and returns the next state that accepts the given character.
        Raises NotImplementedError if no such state exists.
        """
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

class StartState(State):
    """
    Class for Sart State
    """
    def __init__(self):
        """
        Initializes the initial (start) state of the FSM.
        """
        super().__init__()
        self.next_states = []

    def check_self(self, char):
        """
        Always returns False, as the start state does
        not process characters itself.
        """
        return False

class TerminationState(State):
    """
    Initializes the final (termination) state.
    """
    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        """
        Always returns False for the termination state.
        """
        return False

class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        """
        Initializes the state responsible for matching any single character.
        """
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        """
        Always returns True, as the '.' symbol accepts anything.
        """
        return True

class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        """
        Initializes the state for a specific ASCII character.
        """
        super().__init__()
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        """
        Checks if the current character matches the state's stored character.
        """
        return self.curr_sym == curr_char

class StarState(State):
    """
    Class for Star State
    """
    def __init__(self, checking_state: State):
        """
        Initializes the state for the '*' quantifier
        (zero or more repetitions).
        """
        super().__init__()
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        """
        Checks the character against the nested state or
        subsequent states.
        """
        if self.checking_state.check_self(char):
            return True
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False

class PlusState(State):
    """
    Class for Plus State
    """
    def __init__(self, checking_state: State):
        """
        Initializes the state for the '+' quantifier
        (one or more repetitions).
        """
        super().__init__()
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        """
        Checks the character against the nested state
        (requires at least one match).
        """
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    Checks if the provided string matches the regular expression
    using Depth-First Search (DFS) with a stack.
    """
    def __init__(self, regex_expr: str) -> None:
        """
        Builds the Finite State Machine (FSM) based on the provided
        regular expression.
        """
        self.curr_state: State = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)

        if prev_state.next_states:
            self.last_state = prev_state.next_states[-1]
        else:
            self.last_state = self.curr_state

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        """
        Processes the next regex token and creates the corresponding
        state object.
        """
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                if tmp_next_state in prev_state.next_states:
                    prev_state.next_states.remove(tmp_next_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                if tmp_next_state in prev_state.next_states:
                    prev_state.next_states.remove(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

        if new_state and next_token not in ("*", "+"):
            if tmp_next_state != prev_state and not isinstance(tmp_next_state, StartState):
                tmp_next_state.next_states.append(new_state)

        return new_state

    def check_string(self, checking_str: str) -> bool:
        """
        Checks if the provided string matches the regular expression
        using Depth-First Search (DFS) with a stack.
        """
        stack = [(0, self.curr_state)]
        visited = set()
        while stack:
            str_idx, current_state = stack.pop()
            state_key = (str_idx, current_state)
            if state_key in visited:
                continue
            visited.add(state_key)
            if str_idx == len(checking_str):
                if current_state == self.last_state:
                    return True
                for next_state in current_state.next_states:
                    if next_state == self.last_state and isinstance(next_state, StarState):
                        return True
                continue
            char = checking_str[str_idx]
            if current_state == self.curr_state:
                stack.append((str_idx + 1, self.curr_state))
            if isinstance(current_state, (StarState, PlusState)):
                if current_state.checking_state.check_self(char):
                    stack.append((str_idx + 1, current_state))
            for nxt in current_state.next_states:
                if nxt.check_self(char):
                    stack.append((str_idx + 1, nxt))
        return False

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))        # True
    print(regex_compiled.check_string("meow"))        # False
