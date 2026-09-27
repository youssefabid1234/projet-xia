"""Relecture et banque orale du chapitre 11, pages PDF 69–76.

Les réponses des applications sont des résolutions éditoriales des exemples
du cours. Les deux résultats admis ne donnent pas lieu à une preuve demandée.
"""
import hashlib
import json
from pathlib import Path

from scripts.index_cours import write_json

ROOT = Path(__file__).resolve().parents[1]

# Formules relues dans le support ; le brut et les coordonnées restent conservés.
TEXTES = {
    "11.1.1": r"Une équation différentielle linéaire d'ordre $r$ est de la forme $\sum_{k=0}^r a_k(x)y^{(k)}(x)=b(x)$, où $a_r$ n'est pas identiquement nulle. Les coefficients et l'inconnue sont à valeurs dans $\mathbb K=\mathbb R$ ou $\mathbb C$. On définit de même les équations à plusieurs fonctions inconnues et les systèmes linéaires par des relations affines entre leurs dérivées.",
    "11.1.2": r"Sur un intervalle $I$, si $y_p$ est une solution particulière de $L(y)=b$, l'ensemble des solutions est $S=y_p+S_0$, où $S_0=\{y:L(y)=0\}$ est un espace vectoriel. Éléments de preuve : par linéarité, $L(y)=b$ équivaut à $L(y-y_p)=0$ ; la fonction nulle et toute combinaison linéaire de solutions homogènes appartiennent à $S_0$.",
    "11.1.3": r"Si $b=b_1+b_2$ et si $L(y_1)=b_1$, $L(y_2)=b_2$, alors $y_1+y_2$ est une solution particulière de $L(y)=b$. Éléments de preuve : $L(y_1+y_2)=L(y_1)+L(y_2)=b_1+b_2$ par linéarité de la dérivation.",
    "11.2.1": r"Si $a:I\to\mathbb K$ est continue et $A$ une primitive de $a$, les solutions de $y'=a(x)y$ sur l'intervalle $I$ sont exactement $y(x)=Ce^{A(x)}$, $C\in\mathbb K$. Éléments de preuve : poser $z=ye^{-A}$ ; alors $z'=e^{-A}(y'-ay)$, donc $z$ est constante si et seulement si $y$ est solution.",
    "11.2.4": r"Pour $y'=a(x)y+b(x)$, avec $a,b$ continues sur un intervalle et $A'=a$, rechercher $y=C(x)e^{A(x)}$. Substitution : $C'=be^{-A}$ ; on obtient $C$ par primitivation. Ajouter à une solution particulière toutes les solutions de l'équation homogène.",
    "11.2.5": r"1. Résoudre $y'=2y+\sin x+e^x+x$ sur $\mathbb R$. 2. Résoudre $y'=-y/x+\arctan x$ sur $\mathbb R_+^*$.",
    "11.2.7": r"1. Si $a,b$ sont constants et $a\ne0$, la constante $-b/a$ résout $y'=ay+b$. 2. Pour $y'=ay+be^{\alpha x}$, chercher $y=ce^{\alpha x}$ : le coefficient doit satisfaire $(\alpha-a)c=b$. Note de relecture : la condition $a\ne0$, nécessaire à la division, est implicite dans le premier exemple du PDF.",
    "11.2.8": r"Si $a,b:I\to\mathbb K$ sont continues sur un intervalle $I$, pour tout $(x_0,y_0)\in I\times\mathbb K$, il existe une unique solution de $y'=ay+b$ telle que $y(x_0)=y_0$. Éléments de preuve : une solution générale est $y_p+Ce^A$ ; la condition initiale impose l'unique constante $C=(y_0-y_p(x_0))e^{-A(x_0)}$.",
    "11.2.9": r"Résoudre sur $\mathbb R$ : 1. $\sqrt{|x|}\,y'=y$. 2. $xy'=y$. Résoudre sur les intervalles où le coefficient de $y'$ ne s'annule pas ; raccorder par continuité, vérifier la dérivabilité puis l'équation aux points de raccordement.",
    "11.2.10": r"Pour $a,b\in\mathbb K$, $a\ne0$, les solutions de $y'=ay+b$ sont $y(x)=Ce^{ax}-b/a$. Celle vérifiant $y(x_0)=y_0$ est $y(x)=(y_0+b/a)e^{a(x-x_0)}-b/a$. Éléments de preuve : appliquer la structure affine avec la solution particulière constante $-b/a$. Note de relecture : le PDF omet la condition $a\ne0$. Si $a=0$, l'équation est $y'=b$ et $y(x)=y_0+b(x-x_0)$.",
    "11.3.1": r"Pour $y''+a(x)y'+b(x)y=f(x)$, connaissant une solution $y_0$ de l'homogène, poser $y=y_0z$. Sur un intervalle où $y_0\ne0$, on obtient $y_0z''+(2y_0'+ay_0)z'=f$. Résoudre l'équation du premier ordre en $z'$, puis primitiver pour obtenir $z$. On obtient deux constantes ; vérifier les raccordements si $y_0$ s'annule.",
    "11.3.3": r"Pour $a,b\in\mathbb C$, poser $P(X)=X^2+aX+b$ et $\Delta=a^2-4b$. Si $\Delta\ne0$, les solutions complexes de $y''+ay'+by=0$ sont $ce^{r_1x}+de^{r_2x}$ où $r_1,r_2$ sont les racines de $P$. Si $\Delta=0$, elles sont $(c+dx)e^{rx}$, $r=-a/2$. Dans les deux cas $c,d\in\mathbb C$.",
    "11.3.4": r"Le polynôme $P(X)=X^2+aX+b$ est appelé polynôme caractéristique de $y''+ay'+by=0$.",
    "11.3.6": r"Si $a,b$ sont réels, l'ensemble $S_{\mathbb R}$ des solutions réelles de $y''+ay'+by=0$ est $\{\operatorname{Re}y:y\in S_{\mathbb C}\}$. Éléments de preuve : la partie réelle commute à la dérivation et aux multiplications par les coefficients réels ; réciproquement une solution réelle est une solution complexe égale à sa propre partie réelle.",
    "11.3.7": r"Pour $a,b\in\mathbb R$, poser $\Delta=a^2-4b$. Si $\Delta>0$, les solutions réelles sont $ce^{r_1x}+de^{r_2x}$. Si $\Delta=0$, elles sont $(cx+d)e^{rx}$. Si $\Delta<0$, elles sont $e^{\alpha x}(c\cos(\omega x)+d\sin(\omega x))$, avec $\alpha=-a/2$, $\omega=\sqrt{-\Delta}/2$. Les constantes $c,d$ sont réelles. Dans le dernier cas on peut aussi écrire $Ae^{\alpha x}\cos(\omega x-\varphi)$, ou une forme décalée en $x-x_0$ adaptée aux conditions initiales.",
    "11.3.8": r"Résultat admis. Pour $y''+ay'+by=Q(x)e^{\lambda x}$, avec $Q\in\mathbb C[X]$ non nul, si $m$ est la multiplicité de $\lambda$ dans le polynôme caractéristique ($m=0$ si ce n'est pas une racine), il existe une solution particulière $x^mR(x)e^{\lambda x}$ où $\deg R=\deg Q$. Le résultat s'étend aux ordres supérieurs. Note : pour $Q=0$, prendre la solution nulle ; le degré du polynôme nul n'intervient pas.",
    "11.3.9": r"Résoudre sur $\mathbb R$ : 1. $y''+2y'+y=e^x$. 2. $y''+y'+y=\sin x$.",
    "11.3.10": r"Résultat admis. Soient $a,b\in\mathbb R$ constants, $I$ un intervalle réel, $f:I\to\mathbb R$ continue, $x_0\in I$ et $(y_0,y_1)\in\mathbb R^2$. Il existe une unique solution de $y''+ay'+by=f(x)$ telle que $y(x_0)=y_0$ et $y'(x_0)=y_1$.",
}


def main():
    payload = json.loads((ROOT / "data/cours_edl_passages.json").read_text(encoding="utf-8"))
    questions = []

    def q(source, nature, question, reponse=None, references=None, priorite=1):
        questions.append(dict(source=source, nature=nature, priorite=priorite,
                              question=question, reponse_attendue=reponse or TEXTES[source]))
        if references:
            liens[source] = references

    liens_path = ROOT / "data/notions_questions.json"
    liens = json.loads(liens_path.read_text(encoding="utf-8"))
    q("11.1.1", "definition", "Qu'appelle-t-on équation différentielle linéaire d'ordre $r$ ?")
    q("11.1.2", "definition", "Qu'appelle-t-on équation homogène associée à une équation différentielle linéaire ?", r"À $L(y)=b$, on associe $L(y)=0$ : on conserve les coefficients et on remplace le second membre par zéro.")
    q("11.3.4", "definition", "Définissez le polynôme caractéristique de $y''+ay'+by=0$.")
    q("11.2.8", "definition", "Qu'est-ce qu'un problème de Cauchy pour une équation du premier ordre ?", r"Il s'agit de chercher une solution de l'équation sur un intervalle $I$ qui vérifie une condition initiale prescrite $y(x_0)=y_0$, avec $x_0\in I$.")
    for source, question in {
        "11.1.2": "Décrivez la structure de l'ensemble des solutions d'une équation différentielle linéaire possédant une solution particulière.",
        "11.1.3": "Énoncez le principe de superposition pour une équation différentielle linéaire.",
        "11.2.1": "Donnez toutes les solutions de $y'=a(x)y$ sur un intervalle, en précisant les hypothèses.",
        "11.2.4": "Exposez la méthode de variation de la constante pour $y'=a(x)y+b(x)$.",
        "11.2.8": "Énoncez le théorème de Cauchy-Lipschitz pour une équation linéaire du premier ordre.",
        "11.2.10": "Résolvez $y'=ay+b$ à coefficients constants avec $y(x_0)=y_0$, en distinguant $a=0$ et $a\ne0$.",
        "11.3.3": "Donnez toutes les solutions complexes de $y''+ay'+by=0$ selon les racines caractéristiques.",
        "11.3.6": "Comment obtenir les solutions réelles d'une équation homogène à coefficients réels à partir des solutions complexes ?",
        "11.3.7": "Donnez toutes les solutions réelles de $y''+ay'+by=0$ selon le discriminant.",
        "11.3.8": r"Quelle forme de solution particulière cherche-t-on pour un second membre $Q(x)e^{\lambda x}$ ? Précisez le rôle de la multiplicité.",
        "11.3.10": "Énoncez le théorème de Cauchy-Lipschitz pour une équation linéaire du second ordre à coefficients constants.",
    }.items():
        q(source, "theoreme", question)
    for source, question in {
        "11.1.2": "Démontrez le théorème de structure des solutions d'une équation différentielle linéaire.",
        "11.1.3": "Démontrez le principe de superposition.",
        "11.2.1": "Démontrez la formule des solutions de $y'=a(x)y$ sans diviser par $y$.",
        "11.2.8": "Démontrez l'existence et l'unicité pour le problème de Cauchy linéaire du premier ordre à partir de la solution générale.",
        "11.3.6": "Démontrez le lien entre solutions réelles et parties réelles des solutions complexes pour une équation homogène à coefficients réels.",
    }.items():
        q(source, "demonstration", question)
    q("11.2.3", "application", r"Résolvez $y'=ay$ sur $\mathbb R$, où $a\in\mathbb R$ est constant.", r"Une primitive de $a$ est $ax$. Toutes les solutions sont $y(x)=Ce^{ax}$, $C\in\mathbb R$.", ["11.2.1"])
    q("11.2.5", "application", r"Résolvez sur $\mathbb R$ : $y'=2y+\sin x+e^x+x$.", r"L'homogène donne $Ce^{2x}$. Par superposition, une solution particulière est $-(2\sin x+\cos x)/5-e^x-x/2-1/4$. Ainsi $y=Ce^{2x}-(2\sin x+\cos x)/5-e^x-x/2-1/4$, $C\in\mathbb R$.", ["11.1.3", "11.2.1", "11.2.4"])
    q("11.2.7", "application", r"Pour $a,b,\alpha\in\mathbb R$, cherchez une solution particulière de $y'=ay+be^{\alpha x}$, en distinguant $\alpha=a$.", r"Si $\alpha\ne a$, prendre $y_p=\frac{b}{\alpha-a}e^{\alpha x}$. Si $\alpha=a$, la variation de la constante donne $C'=b$, donc $y_p=bxe^{ax}$. Dans les deux cas, ajouter $Ce^{ax}$ pour la solution générale.", ["11.2.4", "11.2.1"])
    q("11.2.9", "application", r"Résolvez $xy'=y$ sur $\mathbb R$ en justifiant le raccordement en zéro.", r"Sur chaque demi-droite, $y=C_-x$ ou $C_+x$. L'équation impose $y(0)=0$, ce qui assure la continuité. La dérivabilité en zéro impose $C_-=C_+$. Toutes les solutions sur $\mathbb R$ sont donc $y(x)=Cx$.", ["11.2.1", "11.2.8"])
    q("11.3.9", "application", r"Résolvez sur $\mathbb R$ : $y''+2y'+y=e^x$ et $y''+y'+y=\sin x$.", r"1. Le polynôme caractéristique est $(X+1)^2$ ; $y_h=(C+Dx)e^{-x}$. Comme $1$ n'est pas racine, $y_p=e^x/4$. 2. Les racines sont $-1/2\pm i\sqrt3/2$ ; $y_h=e^{-x/2}(C\cos(\sqrt3x/2)+D\sin(\sqrt3x/2))$. Une solution particulière est $-\cos x$. Dans chaque cas, $y=y_h+y_p$ et $C,D\in\mathbb R$.", ["11.3.7", "11.3.8"])
    write_json(ROOT / "scripts/transcriptions/cours_edl.json", {
        "pdf_sha256": hashlib.sha256((ROOT / "data/cours/analyse.pdf").read_bytes()).hexdigest(),
        "passages": TEXTES,
    })
    write_json(ROOT / "data/questions_cours_edl.json", {
        "version": 1, "chapitre": payload["chapitre"], "index": "data/cours_edl_index.json",
        "note_editoriale": "Applications résolues pour la banque ; résultats admis exclus des démonstrations. Conditions de division explicitées.",
        "questions": questions,
    })
    write_json(liens_path, liens)


if __name__ == "__main__":
    main()
