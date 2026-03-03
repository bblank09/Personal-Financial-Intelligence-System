class RecommendationService:
    @staticmethod
    def generate_recommendations(saving_rate, total_income, total_expense):
        recommendations = []

        if total_income == 0:
            if total_expense > 0:
                recommendations.append("You have expenses but no income this month. Review your cash reserves.")
            else:
                recommendations.append("No financial activity recorded yet for this month.")
            return recommendations

        if saving_rate < 0:
            recommendations.append("Critical: You are spending more than you earn. Review all recent expenses and cut non-essentials immediately.")
        elif saving_rate < 0.1:
            recommendations.append("Warning: Your saving rate is below 10%. Try to reduce entertainment or food delivery expenses by 15%.")
        elif saving_rate < 0.2:
            recommendations.append("On Track: You are saving nicely. Aim to push your savings above 20% for better long-term security.")
            recommendations.append("Consider investing a portion of your savings.")
        else:
            recommendations.append("Excellent: You are saving a healthy percentage of your income.")
            recommendations.append("Look into diversified investment options to grow your wealth.")

        return recommendations
