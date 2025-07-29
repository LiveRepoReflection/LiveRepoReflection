class SkylineMerger:
    def __init__(self):
        self.skyline = []

    def add_building(self, left, right, height):
        building_skyline = [[left, height], [right, 0]]
        if not self.skyline:
            self.skyline = building_skyline
        else:
            self.skyline = self._merge_skylines(self.skyline, building_skyline)

    def get_skyline(self):
        return self.skyline

    def _merge_skylines(self, sky1, sky2):
        i, j = 0, 0
        h1, h2 = 0, 0
        merged = []
        while i < len(sky1) and j < len(sky2):
            if sky1[i][0] < sky2[j][0]:
                x = sky1[i][0]
                h1 = sky1[i][1]
                max_h = max(h1, h2)
                self._append_keypoint(merged, x, max_h)
                i += 1
            elif sky1[i][0] > sky2[j][0]:
                x = sky2[j][0]
                h2 = sky2[j][1]
                max_h = max(h1, h2)
                self._append_keypoint(merged, x, max_h)
                j += 1
            else:
                x = sky1[i][0]
                h1 = sky1[i][1]
                h2 = sky2[j][1]
                max_h = max(h1, h2)
                self._append_keypoint(merged, x, max_h)
                i += 1
                j += 1

        while i < len(sky1):
            self._append_keypoint(merged, sky1[i][0], sky1[i][1])
            i += 1

        while j < len(sky2):
            self._append_keypoint(merged, sky2[j][0], sky2[j][1])
            j += 1

        return merged

    def _append_keypoint(self, skyline, x, height):
        if not skyline or skyline[-1][1] != height:
            skyline.append([x, height])