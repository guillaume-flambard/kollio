# Owner adds a participant from the interface (#66)

The owner-add flow existed only in the API. The initiative's team panel now
offers the owner a form: pick a colleague from the workspace members, choose
a participation (decision maker, contributor, observer; owner stays
reserved) and a business function, then add. The member list comes from
`GET /workspaces/{workspace_id}/members` through a BFF route; the add goes
to the existing `POST /ideas/{idea_id}/members` through a BFF route. A
non-owner sees no form (the application form is theirs instead).

Labels come from the catalogs in both locales. No technical vocabulary is
shown: participation and function only.

Covered by browser checks TEAM-07 (owner adds Thomas as decision maker in
sales, the posted payload is asserted) and TEAM-08 (a member sees no form).
