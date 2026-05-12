from backend.services.intent_classifier import IntentResult


class ResponseBuilder:
    def build_chat_response(
        self,
        query: str,
        session_id: str,
        intent_result: IntentResult,
        search_results: list[dict],
        recommendations: list[dict],
        policy_hits: list[dict],
        store_profile: dict,
    ) -> dict:
        intent = intent_result.intent
        recommendation_reasons = [item["reason"] for item in recommendations if item.get("reason")]
        response_type = "sales_guidance"
        fallback = False

        if intent == "greeting":
            answer = (
                f"Hi! I’m the {store_profile['assistant_name']} for {store_profile['business_name']}. "
                "I can help with product discovery, bundle ideas, Facebook Marketplace purchase steps, "
                "and store policy questions."
            )
            next_action = "Tell me what kind of item you want, like a collectible, bundle, or gift idea."
            products = recommendations[:2] or search_results[:2]
            response_type = "welcome"
        elif intent in {"shipping_pickup", "payment", "purchase_help", "general_help"}:
            answer = policy_hits[0]["content"] if policy_hits else (
                "I can help with store policies, payment methods, pickup, shipping, and Marketplace purchase guidance."
            )
            next_action = "If you have a product in mind, mention it and I can pair the policy answer with the right listing."
            products = search_results[:2]
            response_type = "policy"
        elif intent == "bundle_inquiry":
            answer = (
                "I found a bundle-focused match that may fit what you’re looking for."
                if recommendations
                else "I can help compare bundle options and suggest the best pairing."
            )
            next_action = "Open the bundle listing or ask me to compare it against another item."
            products = recommendations or search_results[:3]
            response_type = "bundle_support"
        elif intent == "availability":
            if search_results:
                top_product = search_results[0]["product"]
                answer = (
                    f"The strongest availability match is {top_product.title}. "
                    f"Current status: {top_product.availability}."
                )
            else:
                answer = "I can check which listing best matches the item you want and point you to its current availability status."
            next_action = "Tell me the exact product name if you want the fastest availability lookup."
            products = search_results[:3]
            response_type = "availability"
        elif intent == "recommendation":
            if recommendations:
                top_recommendation = recommendations[0]
                answer = (
                    f"My top recommendation is {top_recommendation['product'].title} "
                    f"because it {top_recommendation['reason']}."
                )
            else:
                answer = "I can recommend items based on interests like Pokemon, collectibles, gifts, kids, or electronics."
            next_action = "Open one of the recommendations below or refine the request with who it’s for."
            products = recommendations or search_results[:3]
            response_type = "recommendation"
        elif intent == "product_search":
            if search_results:
                top_match = search_results[0]
                answer = (
                    f"The closest match I found is {top_match['product'].title}. "
                    f"It scored well because it lines up with {', '.join(top_match['matched_terms']) or 'your search terms'}."
                )
            else:
                answer = "I can search the catalog semantically and surface the closest product matches."
            next_action = "Use the product links below or ask for similar alternatives."
            products = search_results[:3] or recommendations[:3]
            response_type = "product_search"
        else:
            answer = (
                "I’m not fully confident yet, but I can still help with products, recommendations, "
                "bundles, payment methods, pickup, shipping, and Facebook Marketplace purchase steps."
            )
            next_action = "Try asking for a product type, who the item is for, or how you want to buy."
            products = recommendations[:2] or search_results[:2]
            response_type = "fallback"
            fallback = True

        return {
            "session_id": session_id,
            "intent": intent,
            "confidence": intent_result.confidence,
            "answer": answer,
            "next_action": next_action,
            "response_type": response_type,
            "products": products,
            "policy_hits": policy_hits,
            "recommendation_reasons": recommendation_reasons[:3],
            "fallback": fallback,
        }
