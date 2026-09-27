"""Routes du tableau (tablette -> lecture -> vérification -> state.set_board). [lane B]"""

from fastapi import APIRouter

router = APIRouter(tags=["tableau"])

# TODO(B) : route qui reçoit le PNG du tableau, appelle
# board_reader.read_board puis verifier.check_line, et finit par state.set_board.
