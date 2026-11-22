# Guide d'annotation NER (français, presse de Djibouti)

On annote le texte brut, à la main, sans modèle. Une entité = un début, une fin (en caractères, fin exclue) et un type. Ces règles sont appliquées partout de la même façon.

## Les 5 types

| Type | Définition | Exemples |
|---|---|---|
| ORG | institution, ministère, fédération, entreprise, organisation, organe constitué | Fédération djiboutienne de football, ministère de la Jeunesse et de la Culture |
| LOC | lieu : pays, ville, quartier, localité, bâtiment ou site nommé | Djibouti, Tadjourah, Ardo Bankoualé, Théâtre des Salines |
| PER | personne, par son nom propre | Louise Mushikiwabo, Radwan Abdillahi Bahdon |
| DATE | date ou moment ancré dans le calendrier | lundi 5 octobre, 2026-2027 |
| FORMATION | diplôme, master, filière | master en santé publique |

## Règles générales
- **Une seule annotation par endroit** : pas de chevauchement, pas d'entité dans une entité. On prend la plus longue.
  Ex. : « Fédération djiboutienne de football » = 1 ORG (on n'annote pas « Djibouti » dedans).
- **Le nom propre seulement** : pas d'article (« le », « les ») ni de ponctuation.
- **Doute** : on annote selon la règle la plus proche et on met `a_verifier = oui` avec une remarque.

## Cas difficiles

**Mentions courtes** : « la Fédération », « l'Organisation », « le Comité » (nom court avec article, sans le nom complet) → non annotées. On annote le nom complet seulement.

**Fonction ou personne**
- Une fonction seule n'est pas une entité : « le ministre de l'Agriculture » → rien.
- Le nom qui suit est PER : « Radwan Abdillahi Bahdon » → PER.

**Titre devant un nom** : le titre n'est **pas** dans PER. On annote le nom seul.
- « Dr Maad Nasser Mohamed » → PER = « Maad Nasser Mohamed ».
- « Me Abeyazide » → PER = « Abeyazide ».
- « l'inspecteur général Moussa Ali Mohamed » → PER = « Moussa Ali Mohamed ».

**ORG**
- Le mot « ministère » / « secrétariat » fait partie de l'entité : « ministère de la Jeunesse et de la Culture » = 1 ORG ; « Secrétariat d'État chargé des Sports » = 1 ORG.
- Organe d'une organisation (« Comité directeur », « Comité ad hoc ») → ORG, `a_verifier = oui`.
- ORG qui contient un lieu : une seule ORG, on n'annote pas le lieu dedans. « Coopérative artisanale des femmes d'Ardo », « Conseil régional de Tadjourah » → 1 ORG chacune.
- « Programme élargi de vaccination » → ORG, `a_verifier = oui`.
- Groupement d'États (« BRICS », « G20 ») → ORG, `a_verifier = oui`.
- « Assemblée générale extraordinaire » est une réunion, donc un événement → non annoté.

**Sigles** : deux annotations, même type, quand la forme longue et le sigle sont écrits.
- « Fédération djiboutienne de football (FDF) » → ORG « Fédération djiboutienne de football » + ORG « FDF ».
- Un sigle seul (OIF, OMS) → 1 ORG. MENFOP est le sigle d'un ministère → ORG.

**Lieux**
- « Djibouti » est LOC partout (pays, ville ou gouvernement). « République de Djibouti » = 1 LOC.
- « Théâtre des Salines » : lieu où se passe l'événement → LOC.
- « école de la Zone portuaire Sud » → LOC = « Zone portuaire Sud » seulement (« école » est un nom commun).
- Un nom commun descriptif (école, aéroport) n'est pas annoté ; on garde le nom propre : « aéroport international de Djibouti » → LOC = « Djibouti ».
- Les adjectifs (« djiboutien ») ne sont pas annotés.

**Dates**
- DATE : jour + date (« lundi 5 octobre »), plage (« 30 et 31 août 2026 », « 6, 7 et 8 octobre »), date simple (« 7 octobre »), année ou année scolaire (« 2026-2027 »). On n'inclut ni « les » ni « jusqu'au ».
- Jour de semaine seul (« lundi ») → DATE.
- « jeudi soir » → DATE entière, `a_verifier = oui`.
- Pas de DATE pour les dates relatives sans repère : « cette année », « aujourd'hui », « l'an dernier ».
- « fin de », « début de », « mi- » + date : exclus de la DATE. On annote « mars 2026 », pas « fin de mars 2026 ».

**Événements** : hors types, donc non annotés (« Activités Estivales 2026 », « Challenge intercommunautaire culturel et sportif », « Mission économique de la Francophonie en Afrique de l'Est »). On n'annote rien à l'intérieur du nom de l'événement (règle « pas d'entité dans une entité »).

**Hors types** : les textes officiels et les programmes de loi (« Defence Procurement Procedure ») ne sont pas annotés ; les notions géopolitiques (« Sud global ») non plus.

**FORMATION** : le nom du diplôme ou de la filière, sans le verbe (« obtenir un master en droit » → « master en droit »). Si le corpus n'a aucun cas, on n'en invente pas.

## Notes pour l'évaluation
- `fr_core_news_sm` ne prédit que PER, ORG, LOC et MISC. Il ne prédit ni DATE ni FORMATION.
- DATE sera donc évaluée à part (baseline avec règles `EntityRuler`).
