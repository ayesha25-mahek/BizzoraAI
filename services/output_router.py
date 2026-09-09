class OutputRouter:

    def __init__(self):

        self.generators = {}

    def register(self, output_type, generator):

        self.generators[output_type] = generator

    def get_available_outputs(self):

        return list(self.generators.keys())

    def route(self, content_model, output_request):

        results = {}

        for output_type in output_request.outputs:

            print(
                f"\nRouting output: {output_type}"
            )

            generator = self.generators.get(
                output_type
            )

            if generator is None:

                print(
                    f"⚠️ No generator registered "
                    f"for: {output_type}"
                )

                results[output_type] = {
                    "status": "not_implemented",
                    "message": (
                        f"No generator available "
                        f"for {output_type}"
                    )
                }

                continue

            try:

                result = generator.generate(
                    content_model,
                    output_request
                )

                results[output_type] = {
                    "status": "success",
                    "result": result
                }

            except Exception as e:

                print(
                    f"❌ {output_type} generation failed:"
                )

                print(e)

                results[output_type] = {
                    "status": "failed",
                    "error": str(e)
                }

        return results