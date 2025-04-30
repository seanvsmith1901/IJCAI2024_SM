class SimulationResult:
    def __init__(self):
        self.algorithm_type = None
        self.coefficient_of_variation = None
        self.cooperation = None
        self.sums_per_round = {}
        self.total_average_increase = None
        self.cumulative_average_score = []

    @staticmethod
    def parse_number_list(data: str, as_float=False):
        if not data:
            return []
        if as_float:
            return [float(x) for x in data.strip().split(',') if x]
        return [int(x) for x in data.strip().split(',') if x]

    @staticmethod
    def parse_sums_per_round(line: str) -> dict[int, list[int]]:
        """
        Parses the 'sumsPerRound' line in the format:
        sumsPerRound: key1: v1,v2,...; key2: v1,v2,...; ...
        """
        if not line.startswith("sumsPerRound:"):
            raise ValueError("Line does not start with 'sumsPerRound:'")

        result = {}
        data = line[len("sumsPerRound:"):].strip()

        if not data:
            return result

        entries = data.split(';')
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            if ':' not in entry:
                raise ValueError(f"Malformed entry: {entry}")

            key_str, values_str = entry.split(':', 1)
            key = int(key_str.strip())
            values = [int(v) for v in values_str.strip().split(',') if v.strip()]
            result[key] = values

        return result

    @classmethod
    def from_file(cls, filepath: str):
        result = cls()
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("algorithmType:"):
                    result.algorithm_type = int(line.split(':')[1].strip())
                elif line.startswith("coefficientOfVariation:"):
                    result.coefficient_of_variation = float(line.split(':')[1].strip())
                elif line.startswith("cooperation:"):
                    result.cooperation = float(line.split(':')[1].strip())
                elif line.startswith("sumsPerRound:"):
                    result.sums_per_round = cls.parse_sums_per_round(line)
                elif line.startswith("totalAverageIncrease:"):
                    result.total_average_increase = float(line.split(':')[1].strip())
                elif line.startswith("cumulativeAverageScore:"):
                    data = line.split(':', 1)[1].strip()
                    result.cumulative_average_score = cls.parse_number_list(data, as_float=True)
                else:
                    print(f"Warning: Unrecognized line: {line}")
        return result
