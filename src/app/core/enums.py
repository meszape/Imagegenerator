from enum import StrEnum
class Provider(StrEnum): openai='openai'; gemini='gemini'
class SafetyProfile(StrEnum): strict='strict'; balanced='balanced'; permissive='permissive'; custom='custom'
class SessionStatus(StrEnum): active='active'; blocked='blocked'; failed='failed'
class BlockStatus(StrEnum): none='none'; blocked='blocked'; unknown='unknown'
