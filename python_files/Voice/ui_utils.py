def emotion_badge_html(emotion_label: str, bucket: str, conf):
    """
    Returns an HTML badge colored by the (mapped) emotion bucket.
    """
    EMO_BADGE = {
        "happiness": {"bg":"#dcfce7", "fg":"#166534", "bd":"#22c55e"},
        "sadness":   {"bg":"#dbeafe", "fg":"#1e40af", "bd":"#3b82f6"},
        "anger":     {"bg":"#fee2e2", "fg":"#991b1b", "bd":"#ef4444"},
        "neutral":   {"bg":"#f3f4f6", "fg":"#374151", "bd":"#9ca3af"},
    }
    key = (bucket or emotion_label or "neutral").lower()
    if key not in EMO_BADGE:
        key = "neutral"
    c = EMO_BADGE[key]
    conf_txt = f" ({conf:.2f})" if isinstance(conf, (int, float)) else ""
    label_txt = emotion_label or bucket or key
    return f"""
    <span style="
        display:inline-block;padding:6px 10px;border-radius:999px;
        background:{c['bg']}; color:{c['fg']}; border:1px solid {c['bd']};
        font-size:12px; font-weight:600;">
        {label_txt}{conf_txt} → {key}
    </span>
    """
