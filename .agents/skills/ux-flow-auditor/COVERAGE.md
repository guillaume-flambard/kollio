# UX Flow Coverage

Status values: `AUDITED` (linked non-empty evidence) or `UNAUDITED`.
The gate (`scripts/check_ux_coverage.mjs`) fails any `AUDITED` row whose
evidence path is missing or empty.

| Identifier | Locales | Scenarios | Evidence | Status |
|------------|---------|-----------|----------|--------|
| Explorer.Filter.Toolbar.ApplyRole | fr, en | EXPLORER-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-explorer-filter.md | AUDITED |
| Explorer.Filter.Toolbar.ApplyRealism | fr, en | EXPLORER-03, EXPLORER-05 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-explorer-filter.md | AUDITED |
| Explorer.Filter.Toolbar.RenderRealism | fr, en | EXPLORER-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-explorer.md | AUDITED |
| Explorer.Filter.Toolbar.KeepDomainChipsOut | fr, en | EXPLORER-04 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-explorer.md | AUDITED |
| Deposit.Entry.Explorer.OpenForm | fr, en | DEPOSIT-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-deposit.md | AUDITED |
| Deposit.Submit.Form.Confirm | fr, en | DEPOSIT-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-deposit.md | AUDITED |
| Deposit.Submit.Form.Narrate | fr, en | DEPOSIT-03 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-deposit.md | AUDITED |
| Deposit.Submit.Form.Abstain | fr, en | DEPOSIT-04 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-deposit.md | AUDITED |
| Deposit.Verdict.Form.Explain | fr, en | DEPOSIT-05 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-deposit.md | AUDITED |
| WorkspaceArea.Context.Settings.EditProfile | fr, en | SETTINGS-01, SETTINGS-03, SETTINGS-06 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.Context.Settings.ShowEmpty | fr, en | SETTINGS-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.Context.Settings.ManageLists | fr, en | SETTINGS-04, SETTINGS-05 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.Context.Settings.ToggleDetailed | fr, en | SETTINGS-07 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.Onboarding.Settings.AnswerSteps | fr, en | ONBOARD-01, ONBOARD-02, ONBOARD-03, ONBOARD-06 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.Onboarding.Settings.Enrich | fr, en | ONBOARD-04, ONBOARD-05 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-settings.md | AUDITED |
| WorkspaceArea.People.Profile.OpenFromTeam | fr, en | PROFILE-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-profiles.md | AUDITED |
| WorkspaceArea.People.Profile.OpenFromExplorer | fr, en | PROFILE-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-profiles.md | AUDITED |
| IdeaDetail.Experiments.Panel.HoldAtWidth | fr | RESP-375, RESP-768 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| WorkspaceArea.Context.Settings.HoldAtWidth | fr | RESP-375, RESP-768 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| Deposit.Submit.Form.HoldAtWidth | fr | RESP-375, RESP-768 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| Deposit.Submit.Form.NarrateAtPhone | fr | RESP-narration | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| WorkspaceArea.Navigation.TopBar.Open | fr | NAV-mobile | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| Explorer.Filter.Rail.FitAtPhone | fr | NAV-mobile | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| WorkspaceArea.Navigation.Rail.PersistDesktop | fr | NAV-desktop | .agents/skills/ux-flow-auditor/evidence/2026-09-15-responsive.md | AUDITED |
| Timeline.Proposal.IdeaDetail.Send | fr, en | PROPOSE-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-proposal.md | AUDITED |
| Timeline.Proposal.IdeaDetail.SurfaceConflict | fr, en | PROPOSE-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-proposal.md | AUDITED |
| Initiative.Type.Deposit.Select | fr, en | TYPE-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-initiative-type.md | AUDITED |
| Initiative.Type.IdeaDetail.Change | fr, en | TYPE-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-initiative-type.md | AUDITED |
| Initiative.Type.IdeaDetail.HideFromNonOwner | fr, en | TYPE-03 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-initiative-type.md | AUDITED |
| Timeline.History.IdeaDetail.Render | fr, en | TIMELINE-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-timeline.md | AUDITED |
| IdeaDetail.Experiments.Loop.Create | fr, en | EXPERIMENT-01, EXPERIMENT-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-experiments.md | AUDITED |
| IdeaDetail.Experiments.Loop.Run | fr, en | EXPERIMENT-03, EXPERIMENT-04, EXPERIMENT-05 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-experiments.md | AUDITED |
| IdeaDetail.Experiments.Loop.ConfirmLearning | fr, en | EXPERIMENT-06 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-experiments.md | AUDITED |
| IdeaDetail.Experiments.Loop.HideFromNonMember | fr, en | EXPERIMENT-07 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-experiments.md | AUDITED |
| IdeaDetail.Experiments.Loop.SurfaceRefusal | fr, en | EXPERIMENT-08, EXPERIMENT-09 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-experiments.md | AUDITED |
| IdeaDetail.Team.Panel.ReviewApplication | fr, en | TEAM-01, TEAM-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-team.md | AUDITED |
| IdeaDetail.Team.Panel.Apply | fr, en | TEAM-03 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-team.md | AUDITED |
| IdeaDetail.Team.Panel.AddColleague | fr, en | TEAM-07 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-team.md | AUDITED |
| IdeaDetail.Team.Panel.HideFromMember | fr, en | TEAM-08 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-team.md | AUDITED |
| Timeline.Owner.IdeaDetail.Accept | fr, en | OWNER-01 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-owner-actions.md | AUDITED |
| Timeline.Owner.IdeaDetail.Reject | fr, en | OWNER-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-owner-actions.md | AUDITED |
| Timeline.Owner.IdeaDetail.Rollback | fr, en | OWNER-03 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-owner-actions.md | AUDITED |
| Timeline.Owner.IdeaDetail.HideFromMember | fr | MEMBER-04 | .agents/skills/ux-flow-auditor/evidence/2026-09-15-owner-actions.md | AUDITED |
| WorkspaceArea.People.Profile.RoleLabels | fr, en | PROFILE-01, PROFILE-02 | .agents/skills/ux-flow-auditor/evidence/2026-09-17-i18n-profile-role-render.txt | AUDITED |
| WorkspaceArea.I18n.Catalog.Parity | fr, en | I18N-CATALOG, I18N-DEADKEYS, I18N-FORMATS | .agents/skills/ux-flow-auditor/evidence/i18n-report.md | AUDITED |
| Explorer.Filter.Toolbar.SearchName | fr, en | A11Y-EXPLORER | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| Explorer.Results.Main.Landmark | fr, en | A11Y-EXPLORER | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| Explorer.Results.Search.HoldAtPhone | fr | A11Y-DRAWER | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| Landing.Nav.Landmarks.Name | fr, en | A11Y-LANDING | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| Deposit.Verdict.Form.LiveRegion | fr | A11Y-DEPOSIT | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| IdeaDetail.Team.Panel.ControlNames | fr | A11Y-IDEA-DETAIL | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| WorkspaceArea.People.Profile.HeadingStructure | fr | A11Y-PROFILE | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| WorkspaceArea.Context.Settings.SaveAnnouncement | fr | A11Y-SETTINGS | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
| WorkspaceArea.DecisionInbox.Shell.Landmarks | fr | A11Y-INBOX | .agents/skills/ux-flow-auditor/evidence/a11y-report.md | AUDITED |
