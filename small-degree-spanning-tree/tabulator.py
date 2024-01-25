import pathlib
import json
import sys
import os

# reads the results from results/ and creates a markdown table out of them


def main():
    results = []
    result_files = sorted(
        [filename for filename in os.listdir("results") if filename.endswith(".json")]
    )
    algorithms = ["graph"]

    for filename in result_files:
        with open(os.path.join("results", filename)) as fin:
            try:
                results_data = json.load(fin)
            except Exception:
                print(f"Warning: Failed to read {filename}", file=sys.stderr)
                continue

            result = {
                "filename": filename,
            }
            for algorithm_data in results_data:
                if algorithm_data[0] not in algorithms:
                    algorithms.append(algorithm_data[0])

                result[algorithm_data[0]] = int(algorithm_data[1])

            results.append(result)

    print(f"| File | {'|'.join(algorithms)} |")
    print(f"| --- | {'|'.join(['---' for x in algorithms])} |")

    for result in results:
        print("|", end="")
        print(result["filename"], end="|")

        for algorithm in algorithms:
            if algorithm in result:
                print(result[algorithm], end="|")
            else:
                print(" ", end="|")

        print()


if __name__ == "__main__":
    main()
