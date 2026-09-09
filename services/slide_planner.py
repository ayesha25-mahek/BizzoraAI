import json
import os

class SlidePlanner:

    def create_slide_plan(self, content_model, output_request=None):
        """Alias for create_plan — accepts optional output_request for API compatibility."""
        return self.create_plan(content_model)

    def create_plan(self, content_model):

        slides = []

        title = content_model.get(
            "title",
            "Untitled Presentation"
        )

        summary = content_model.get(
            "summary",
            ""
        )

        key_points = content_model.get(
            "key_points",
            []
        )

        statistics = content_model.get(
            "statistics",
            []
        )

        recommendations = content_model.get(
            "recommendations",
            []
        )

        # --------------------------------------------------
        # TITLE SLIDE
        # --------------------------------------------------

        slides.append({
            "slide_number": 1,
            "type": "title",
            "title": title,
            "content": summary
        })

        # --------------------------------------------------
        # OVERVIEW
        # --------------------------------------------------

        if summary:

            slides.append({
                "slide_number": len(slides) + 1,
                "type": "overview",
                "title": "Overview",
                "content": [summary]
            })

        # --------------------------------------------------
        # KEY POINTS
        # --------------------------------------------------

        if key_points:

            slides.append({
                "slide_number": len(slides) + 1,
                "type": "key_points",
                "title": "Key Points",
                "content": key_points
            })

        # --------------------------------------------------
        # STATISTICS
        # --------------------------------------------------

        if statistics:

            slides.append({
                "slide_number": len(slides) + 1,
                "type": "statistics",
                "title": "Key Statistics",
                "content": statistics
            })

        # --------------------------------------------------
        # RECOMMENDATIONS
        # --------------------------------------------------

        if recommendations:

            slides.append({
                "slide_number": len(slides) + 1,
                "type": "recommendations",
                "title": "Recommendations",
                "content": recommendations
            })

        # --------------------------------------------------
        # CONCLUSION
        # --------------------------------------------------

        slides.append({
            "slide_number": len(slides) + 1,
            "type": "conclusion",
            "title": "Conclusion",
            "content": [
                "Key insights and recommended actions."
            ]
        })

        return slides
    def save_plan(self, slides, filename="slide_plan.json"):

        output_dir = "output/slide_plans"

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        path = os.path.join(
            output_dir,
            filename
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                slides,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\n[SUCCESS] Slide plan saved to: {path}"
        )

        return path

    def print_plan(self, slides):

        print("\n")
        print("=" * 60)
        print("                SLIDE PLAN")
        print("=" * 60)

        for slide in slides:

            print(
                f"\nSlide {slide['slide_number']}: "
                f"{slide['title']}"
            )

            print(
                f"Type: {slide['type']}"
            )

            print(
                f"Content: {slide['content']}"
            )