class PathSmoother:

    def smooth(self, path):
        """
        Removes sharp zigzag turns
        """
        if len(path) <= 2:
            return path

        smooth = [path[0]]

        for i in range(1, len(path)-1):
            prev = smooth[-1]
            curr = path[i]
            nxt = path[i+1]

            if abs(prev.x - nxt.x) + abs(prev.y - nxt.y) < \
               abs(prev.x - curr.x) + abs(prev.y - curr.y):
                continue

            smooth.append(curr)

        smooth.append(path[-1])
        return smooth
    