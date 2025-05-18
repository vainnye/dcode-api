
import logging
from pprint import pprint
from query import Query

logger = logging.getLogger(__name__)

def do_example(page_id: str):
    q = Query()
    q.fetch_form(page_id)

    if q.form:
        print(f"successfully fetched form {page_id}!")

    if input("print raw form params? (y/n): ") == "y":
        pprint(q.form.params)

    q.fill_form()
    
    if input("print payload? (y/n): ") == "y":
        pprint(q.payload)
    
    q.send()

    print(q.response)


def do_example1():
    do_example("chiffre-changement-clavier")

def do_example2():
    do_example("chiffre-changement-clavier")

def do_example3():
    do_example("solveur-aworded")


if __name__ == "__main__":
    do_example2()

# here is an example of the output with the 2nd example:


# successfully fetched form chiffre-changement-clavier!
# print raw form params? (y/n): n
# 
# ---------------------------------------------------------------
# Formulaire: Conversion de Clavier (https://www.dcode.fr/chiffre-changement-clavier)
# Outil pour simuler un changement de clavier d'ordinateur : taper les touches en position P sur un clavier en la même touche en position P mais sur un autre clavier (QWERTY/Android/Mac etc.)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# <<<ciphertext>>> --- Message frappé sur un Clavier:        (textarea)
# ... some text ...
# ciphertext: i q; your biggest night;qre
# <<<layout1>>> --- Depuis le Type de Clavier 1:        (select)
# [auto]: Détection automatique          [azerty]: AZERTY (Français)        [qwerty]: QWERTY (US)
# [dvorak]: DVORAK (US)                  [bepo]: BEPO (FR/EU)               [alphabet]: ABC…XYZ (Alphabet)
# [case]: Changement de Casse (abc⇆ABC)  [android]: Android Appui Prolongé
# layout1: auto
# <<<layout2>>> --- Vers le Type de Clavier 2:        (select)
# [auto]: Détection automatique          [azerty]: AZERTY (Français)        [qwerty]: QWERTY (US)
# [dvorak]: DVORAK (US)                  [bepo]: BEPO (FR/EU)               [alphabet]: ABC…XYZ (Alphabet)
# [case]: Changement de Casse (abc⇆ABC)  [android]: Android Appui Prolongé
# layout2: azerty
# print payload? (y/n): n
# 
# RESPONSE bellow:
# Caption: i q; your bi…qre
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# <<< Result >>> --------------
# qwerty ↦ azerty    i am your biggest nightmare
# mobile ↦ azerty    i qB your biggest nightBqre
# mobile₀₉ ↦ azerty  i qB your biggest nightBqre
# colemak ↦ azerty   l aP omis blttkdf jlthfPask
# workman ↦ azerty   m aP hlie tmggksf jmgdfPaek
# azerty abc⇆ABC     I Q. YOUR BIGGEST NIGHT.QRE
# bepo ↦ azerty      d ,g xrsl ad;;fkj md;:jg,lf
# dvorak ↦ azerty    G XW TSFO NGUUDMK LGUJKWXOD
# ABCD...Z ↦ azerty  o j; bgwk zoùùtlm foùim;jkt
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
