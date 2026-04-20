def rank_designers(project, designers):
    project_skill_ids = set(project.skill_ids())
    project_style_ids = set(project.style_ids())

    ranked = []
    for designer in designers:
        skill_score = _skill_score(project_skill_ids, set(designer.skill_ids()))
        style_score = _style_score(project_style_ids, set(designer.style_ids()))
        budget_score = _budget_score(project.budget_min, project.budget_max, designer.price_min, designer.price_max)
        total_score = round(skill_score + style_score + budget_score, 2)

        ranked.append(
            {
                "designer_id": designer.id,
                "name": designer.user.name if designer.user else "",
                "portfolio_url": designer.portfolio_url,
                "price_min": designer.price_min,
                "price_max": designer.price_max,
                "rating": round(float(designer.rating or 0), 1),
                "score": total_score,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def _skill_score(project_skill_ids, designer_skill_ids):
    if not project_skill_ids:
        return 0.0

    overlap = len(project_skill_ids.intersection(designer_skill_ids))
    return round((overlap / len(project_skill_ids)) * 50, 2)


def _style_score(project_style_ids, designer_style_ids):
    if not project_style_ids:
        return 0.0

    overlap = len(project_style_ids.intersection(designer_style_ids))
    return round((overlap / len(project_style_ids)) * 30, 2)


def _budget_score(project_min, project_max, designer_min, designer_max):
    project_min = float(project_min or 0)
    project_max = float(project_max or 0)
    designer_min = float(designer_min or 0)
    designer_max = float(designer_max or 0)

    if project_max <= 0:
        return 0.0

    if designer_min <= project_max and designer_max >= project_min:
        return 20.0

    if designer_max <= project_max:
        return 16.0

    if designer_min > project_max:
        ratio = project_max / designer_min
        return round(max(0.0, min(20.0, ratio * 20.0)), 2)

    return 10.0
