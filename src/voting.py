from typing import Optional


APPROVE_VOTE = 10
NO_VOTE = 0


def map_vote(vote: Optional[int | str]) -> Optional[int]:
	if vote is None or isinstance(vote, int):
		return vote
	assert isinstance(vote, str), \
		f"`vote` must be a string. Got: \"{vote}\" with type: {type(vote)}."
	match vote.lower():
		case 'reject':
			return -10
		case 'wait':
			return -5
		case 'none' | 'reset':
			return NO_VOTE
		case 'approve_with_suggestions':
			return 5
		case 'approve':
			return APPROVE_VOTE
	return None


def map_int_vote(vote: int) -> str | None:
	match vote:
		case -10:
			return 'REJECT'
		case -5:
			return 'wait'
		case 0:
			return 'reset'
		case 5:
			return 'approve_with_suggestions'
		case 10:
			return 'APPROVE'
	return None


def is_vote_allowed(current_vote: int | None, new_vote: int | None) -> bool:
	"""
	Only vote if the new vote is more rejective (more negative) than the current vote,
	the current vote is not set and the new vote is approve or approve with suggestions.
	This is to avoid approving if someone has already voted.
	"""
	return new_vote is not None \
		and (current_vote is None \
			or new_vote < current_vote \
			or (current_vote == NO_VOTE and new_vote > current_vote))