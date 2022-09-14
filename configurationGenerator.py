import numpy as np
import os
import random
import json
from tqdm import tqdm
from matplotlib import pyplot as plt


DEG2RAD = np.pi / 180
RAD2DEG = 180 / np.pi

BOT_REAR_RADIUS = 2.5
BOT_NOSE_ANGLE = np.pi / 8
BOT_LENGTH = BOT_REAR_RADIUS + BOT_REAR_RADIUS / np.sin(BOT_NOSE_ANGLE)


BOT_APPROX_POLY_POINTS = ((BOT_LENGTH - BOT_REAR_RADIUS, 0),
                          (0.957, 2.310),
                          (-1.389, 2.079),
                          (-2.5, 0),
                          (-1.389, -2.079),
                          (0.957, -2.310),
                          )



def sum_points(p1: tuple, p2: tuple, scale: float = 1) -> tuple:
    return (p1[0] + p2[0] * scale,
            p1[1] + p2[1] * scale)


def rotate_point(p: tuple, c: tuple, a: float) -> tuple:
    a = a * DEG2RAD
    rel = sum_points(p, c, scale=-1)
    rot = (rel[0]*np.cos(a) - rel[1]*np.sin(a),
           rel[0]*np.sin(a) + rel[1]*np.cos(a))
    return sum_points(c, rot)


def get_norm(p: tuple) -> float:
    return (p[0]**2 + p[1]**2)**0.5


def get_distance(p1: tuple, p2: tuple) -> float:
    return get_norm(sum_points(p2, p1, scale=-1))


def get_angle(p1: tuple, p2: tuple) -> float:
    x, y = sum_points(p2, p1, scale=-1)
    return np.arctan2(y, x) * RAD2DEG


def get_nose_point(bot: list) -> tuple:
    nose_offset = BOT_LENGTH - BOT_REAR_RADIUS
    return sum_points(bot[2], rotate_point((nose_offset, 0), (0, 0), bot[1]))


def cross_product(v: tuple, u: tuple) -> float:
    return v[0]*u[1] - v[1]*u[0]


def get_triangle_orientation(p1: tuple, p2: tuple, p3: tuple, eps: float = 1e-9) -> int:
    val = cross_product(sum_points(p2, p1, scale=-1),
                        sum_points(p3, p1, scale=-1))

    if abs(val) <= eps:
        return 0

    if val > 0:
        return 1
    else:
        return -1


def check_point_on_segment(p1: tuple, p2: tuple, q: tuple) -> bool:
    return p1[0] <= q[0] <= p2[0] and p1[1] <= q[1] <= p2[1]


def check_two_segments_intersection(p1: tuple, p2: tuple, q1: tuple, q2: tuple) -> bool:
    o1 = get_triangle_orientation(p1, p2, q1)
    o2 = get_triangle_orientation(p1, p2, q2)
    o3 = get_triangle_orientation(q1, q2, p1)
    o4 = get_triangle_orientation(q1, q2, p2)

    return (((o1 != o2) and (o3 != o4)) or
            ((o1 == 0) and check_point_on_segment(p1, p2, q1)) or
            ((o2 == 0) and check_point_on_segment(q1, q2, p1)) or
            ((o3 == 0) and check_point_on_segment(p1, p2, q2)) or
            ((o4 == 0) and check_point_on_segment(q1, q2, p2)))


def check_bots_intersection(bot1: list, bot2: list) -> bool:
    bot1_points = [sum_points(bot1[2], rotate_point(BOT_APPROX_POLY_POINTS[i], (0, 0), bot1[1])) for i in range(len(BOT_APPROX_POLY_POINTS))]
    bot2_points = [sum_points(bot2[2], rotate_point(BOT_APPROX_POLY_POINTS[i], (0, 0), bot2[1])) for i in range(len(BOT_APPROX_POLY_POINTS))]

    for i in range(0, len(bot1_points)):
        for j in range(0, len(bot2_points)):
            if check_two_segments_intersection(bot1_points[i-1], bot1_points[i], bot2_points[j-1], bot2_points[j]):
                return True
    return False


def F(configuration: list) -> float:
    ans = 0 + 0*1j
    l = len(configuration)
    for i in range(l):
        bot1 = configuration[i]
        nose1 = get_nose_point(bot1)
        for j in range(l):
            bot2 = configuration[j]
            nose2 = get_nose_point(bot2)
            if j == i:
                continue
            ans += np.exp(-get_distance(nose1, nose2) / BOT_LENGTH) * np.exp(8*1j*abs(bot1[1] - bot2[1])*DEG2RAD)
    return np.abs(ans)


class Configuration:
    def __init__(self):
        self.configuration = []
        self.used_ids = [False for i in range(1000)]
        random.seed()
        

    def ClearConfiguration(self):
        self.configuration = []
        self._update_used_ids()

    def AddBot(self, identifier:int = None, angle: float = 0, pos: tuple = (0,0)):
        if identifier is None:
            identifier = self._generateNewId()
        bot = [identifier, angle, pos]
        self.configuration.append(bot)
        self.used_ids[identifier] = True

    def AddBots(self, bots: list = []):
        for i in range(len(bots)):
            bot = bots[i]
            if len(bot) == 3:
                id = bot[0]
                angle = bot[1]
                pos = bot[2]
            else:
                id = None
                angle = bot[0]
                pos = bot[1]
            self.AddBot(identifier=id, angle=angle, pos=pos)


    def AddStructure(self, structure: list, pos: tuple, angle: float):
        rotated_structure = self.RotateBotsAroundPoint(bots=structure, center=(0, 0), angle=angle)
        shifted_structure = self.ShiftBots(bots=rotated_structure, vector=pos)
        self.AddBots(shifted_structure)


    # def AddMiccel(self, pos:tuple = (0,0), angle:float = 0):
    #     angles = [22.5*i + angle for i in range(8)]
    #     nose_offset = BOT_LENGTH - BOT_REAR_RADIUS
    #     centers = [sum_points(pos, rotate_point((nose_offset, 0), (0,0), a)) for a in angles]
    #     angles = [a - 180 for a in angles]
    #     for i in range(8):
    #         self.AddBot(angle=)

    def RotateBotsAroundPoint(self, bots: list = [], center: tuple = (0,0), angle: float = 0):
        rotated_bots = []
        for bot in bots:
            new_center_point = rotate_point(bot[2], center, angle)
            new_nose_point = rotate_point(get_nose_point(bot), center, angle)
            new_nose_angle = get_angle(new_center_point, new_nose_point)
            rotated_bots.append([bot[0], new_nose_angle, new_center_point])
        return rotated_bots

    def ShiftBots(self, bots: list = [], vector: tuple = (0, 0)):
        shifted_bots = []
        for bot in bots:
            new_center_point = sum_points(bot[2], vector)
            shifted_bots.append([bot[0], bot[1], new_center_point])
        return shifted_bots

    def LoadConfiguration(self, filename):
        self.configuration = np.load(filename, allow_pickle=True).tolist()
        self._update_used_ids()

    def SaveConfiguration(self, filename):
        np.save(filename, np.array(self.configuration, dtype=object), allow_pickle=True)

    def AddBotRandomized(self, borders_x: tuple, borders_y: tuple, borders_angle: tuple):
        id = self._generateNewId()
        is_done = False
        iterations = 0
        bot = []
        while not is_done:
            pos = (borders_x[0] + (borders_x[1] - borders_x[0]) * random.random(),
                   borders_y[0] + (borders_y[1] - borders_y[0]) * random.random())
            angle = borders_angle[0] + (borders_angle[1] - borders_angle[0]) * random.random()
            bot = [id, angle, pos]
            bots_to_check = [bot for bot in self.configuration if get_distance(bot[2], pos) <= 2*(BOT_LENGTH - BOT_REAR_RADIUS)]
            #checking intersections
            is_done = True
            for bot_to_check in bots_to_check:
                if check_bots_intersection(bot, bot_to_check):
                    is_done = False
                    break
        self.AddBot(identifier=bot[0], angle=bot[1], pos=bot[2])

    def AddBotRandomizedCircle(self, radius: float, borders_angle: tuple):
        id = self._generateNewId()
        is_done = False
        iterations = 0
        bot = []
        while not is_done:
            r = radius * random.random()
            theta = 360 * random.random()
            pos = (r * np.cos(theta * DEG2RAD),
                   r * np.sin(theta * DEG2RAD))
            angle = borders_angle[0] + (borders_angle[1] - borders_angle[0]) * random.random()
            bot = [id, angle, pos]
            bots_to_check = [bot for bot in self.configuration if get_distance(bot[2], pos) <= 2*(BOT_LENGTH - BOT_REAR_RADIUS)]
            #checking intersections
            is_done = True
            for bot_to_check in bots_to_check:
                if check_bots_intersection(bot, bot_to_check):
                    is_done = False
                    break
        self.AddBot(identifier=bot[0], angle=bot[1], pos=bot[2])


    def AddStructureRandomized(self, structure: list, borders_x: tuple, borders_y: tuple, borders_angle: tuple):
        is_done = False
        bots = []
        while not is_done:
            pos = (borders_x[0] + (borders_x[1] - borders_x[0]) * random.random(),
                   borders_y[0] + (borders_y[1] - borders_y[0]) * random.random())
            angle = borders_angle[0] + (borders_angle[1] - borders_angle[0]) * random.random()
            bots = self.ShiftBots(bots=self.RotateBotsAroundPoint(bots=structure, center=(0, 0), angle=angle), vector=pos)
            # checking intersections
            is_done = True
            for bot in bots:
                bots_to_check = [b for b in self.configuration if
                                 get_distance(b[2], bot[2]) <= 2*(BOT_LENGTH - BOT_REAR_RADIUS)]
                for bot_to_check in bots_to_check:
                    if check_bots_intersection(bot, bot_to_check):
                        is_done = False
                        break
        self.AddStructure(structure=bots, pos=(0, 0), angle=0)

    def AddStructureRandomizedCircle(self, structure: list, radius: float, borders_angle: tuple):
        is_done = False
        bots = []
        while not is_done:
            r = radius * random.random()
            theta = 360 * random.random()
            pos = (r * np.cos(theta * DEG2RAD),
                   r * np.sin(theta * DEG2RAD))
            angle = borders_angle[0] + (borders_angle[1] - borders_angle[0]) * random.random()
            bots = self.ShiftBots(bots=self.RotateBotsAroundPoint(bots=structure, center=(0, 0), angle=angle), vector=pos)
            # checking intersections
            is_done = True
            for bot in bots:
                bots_to_check = [b for b in self.configuration if
                                 get_distance(b[2], bot[2]) <= 2*(BOT_LENGTH - BOT_REAR_RADIUS)]
                for bot_to_check in bots_to_check:
                    if check_bots_intersection(bot, bot_to_check):
                        is_done = False
                        break
        self.AddStructure(structure=bots, pos=(0, 0), angle=0)

    def GetConfiguration(self):
        return self.configuration

    def _generateNewId(self):
        for id in range(len(self.used_ids)):
            if not self.used_ids[id]:
                return id
        return None

    def _get_config_ids(self):
        return [bot[0] for bot in self.configuration]

    def _get_config_angles(self):
        return [bot[1] for bot in self.configuration]

    def _get_config_positions(self):
        return [bot[2] for bot in self.configuration]

    def _update_used_ids(self):
        identifiers = self._get_config_ids()
        for id in range(len(self.used_ids)):
            self.used_ids[id] = id in identifiers


if __name__ == '__main__':
    if False:
        todo = 'calc'
        if todo == 'gen':
            #isotropic single bots
            '''
            iterations_for_config = 20
            for p in [0.3, 0.4, 0.5]:
                for N in [64]:
                    bot_area = 27.3607
                    S_bots = N*bot_area
                    S_field = S_bots / p
                    side_length = S_field**0.5
                    print(f'N: {N}, p: {p}, side length: {side_length}')
        
                    borders = ((-side_length/2, side_length/2),
                               (-side_length/2, side_length/2))
        
                    borders_angle = (0, 360)
                    config = Configuration()
                    for iter in range(iterations_for_config):
                        config.ClearConfiguration()
                        for i in range(N):
                            config.AddBotRandomized(borders_x = borders[0], borders_y=borders[1], borders_angle=borders_angle)
                        config.SaveConfiguration(f'configurations/isotropic_bots/isotropic_bots_N_{N}_p_{p}_i_{iter}.npy')
            '''
            #isotropic miccels
            struct_micelle = np.load('micelle.npy', allow_pickle=True).tolist()
            iterations_for_config = 20
            for p in [0.05, 0.25]:
                for N_M in [1, 2, 4, 8, 16]:
                    bot_area = 27.3607
                    S_bots = 8 * N_M * bot_area
                    S_field = S_bots / p
                    side_length = S_field ** 0.5
                    print(f'N_M: {N_M}, p: {p}, side length: {side_length}')

                    borders = ((-side_length / 2, side_length / 2),
                               (-side_length / 2, side_length / 2))

                    borders_angle = (0, 360)
                    config = Configuration()
                    for iter in range(iterations_for_config):
                        config.ClearConfiguration()
                        for i in range(N_M):
                            config.AddStructureRandomized(structure=struct_micelle, borders_x=borders[0], borders_y=borders[1], borders_angle=borders_angle)
                        config.SaveConfiguration(f'configurations/isotropic_micelles/isotropic_micelles_Nm_{N_M}_p_{p}_i_{iter}.npy')
        if todo == 'calc':
            directory = 'C:/Users/mkbuz/PycharmProjects/OrderParameterApp/configurations/isotropic_micelles/'
            # directory = 'C:/Users/mkbuz/PycharmProjects/OrderParameterApp/configurations/isotropic_bots/'
            filenames = [filename for filename in os.listdir(directory)]
            files = [directory + filename for filename in os.listdir(directory)]
            # files = ['micelle.npy']
            # configuration = np.load('micelle.npy', allow_pickle=True).tolist()
            # for bot in configuration:
            #     print(get_nose_point(bot))
            # f = F(configuration)
            # print(f)
            # exit(0)
            results = {}
            for i in range(len(files)):
                filename = filenames[i]
                signature = filename[:-4].split('_')
                iter, p, N = int(signature[-1]), float(signature[-3]), int(signature[-5])
                if str(N) not in results.keys():
                    results[str(N)] = {str(p): []}
                else:
                    results[str(N)][str(p)] = []
            for i in range(len(files)):
                filename = filenames[i]
                signature = filename[:-4].split('_')
                iter, p, N = int(signature[-1]), float(signature[-3]), int(signature[-5])
                print(N, p, iter)
                configuration = np.load(files[i], allow_pickle=True).tolist()
                f = F(configuration)
                results[str(N)][str(p)].append((iter, f))

            with open('configurations/results_micelles.json', 'w') as fp:
                json.dump(results, fp, indent=2)

            results_disp = {}
            for N in results.keys():
                results_disp[N] = {}
                for p in results[N].keys():
                    data = [results[N][p][i][1] for i in range(len(results[N][p]))]
                    avg = sum(data) / len(data)
                    disp = np.std(np.array(data, dtype=float))
                    results_disp[N][p] = (avg, disp)

            with open('configurations/results_micelles_avg.json', 'w') as fp:
                json.dump(results_disp, fp, indent=2)
    if False:
        struct_micelle = np.load('micelle.npy', allow_pickle=True).tolist()
        rho = 0.3
        N = [8 * i for i in range(50, 100, 10)]
        realisations_per_params = 100
        mu = [i / 10 for i in range(10 + 1)]
        if False:
            for n in N:
                for m in mu:
                    path = os.path.join('configurations/fitting', f'N_{n}_mu_{m}')
                    os.mkdir(path)
            exit(0)
        configuration = Configuration()
        for n in tqdm(N):
            for m in tqdm(mu):
                for it in range(realisations_per_params):
                    configuration.ClearConfiguration()
                    bot_area = 27.3607
                    S_bots = n * bot_area
                    S_field = S_bots / rho
                    radius = (S_field / np.pi)**0.5
                    for i in range(round(m * n) // 8):
                        configuration.AddStructureRandomizedCircle(structure=struct_micelle, radius=radius, borders_angle=(0, 360))
                    for i in range(round(n*(1-m))):
                        configuration.AddBotRandomizedCircle(radius=radius, borders_angle=(0, 360))
                    configuration.SaveConfiguration(f'configurations/fitting/N_{n}_mu_{m}/{it}.npy')

        configuration = Configuration()
        for n in tqdm(N):
            for m in tqdm(mu):
                for it in range(realisations_per_params):
                    configuration.ClearConfiguration()
                    bot_area = 27.3607
                    S_bots = n * bot_area
                    S_field = S_bots / rho
                    radius = (S_field / np.pi)**0.5
                    for i in range(round(m * n) // 8):
                        configuration.AddStructureRandomizedCircle(structure=struct_micelle, radius=radius, borders_angle=(0, 360))
                    for i in range(round(n*(1-m))):
                        configuration.AddBotRandomizedCircle(radius=radius, borders_angle=(0, 360))
                    configuration.SaveConfiguration(f'configurations/fitting/N_{n}_mu_{m}/{it}.npy')

    if False:
        rho = 0.3
        N = [8 * i for i in range(40, 100, 10)]
        realisations_per_params = 100
        mu = [i / 10 for i in range(10 + 1)]
        with open('configurations/results_fit.json', 'r') as fp:
            results= json.load(fp)
        print(results)
        # for n in N:
        #     for m in mu:
        #         if str(n) not in results.keys():
        #             results[str(n)] = {str(m): []}
        #         else:
        #             results[str(n)][str(m)] = []
        for n in tqdm(N):
            for m in tqdm(mu):
                for it in range(realisations_per_params):
                    configuration = np.load(f'configurations/fitting/N_{n}_mu_{m}/{it}.npy', allow_pickle=True).tolist()
                    f = F(configuration)
                    results[str(n)][str(m)].append(f)
            with open('configurations/results_fit.json', 'w') as fp:
                json.dump(results, fp, indent=2)

    if False:
        N = [8 * i for i in range(10, 100, 10)]
        realisations_per_params = 100
        mu = [i / 10 for i in range(10 + 1)]
        with open('configurations/results_fit.json', 'r') as fp:
            results = json.load(fp)
        results_avg = {}
        for n in N:
            for m in mu:
                if str(m) not in results_avg.keys():
                    results_avg[str(m)] = {str(n): 0}
                else:
                    results_avg[str(m)][str(n)] = 0
        for n in results.keys():
            for m in results[n].keys():
                data = np.array(results[n][m], dtype=float)
                avg = np.average(data)
                std = np.std(data)
                results_avg[m][n] = (avg, std)
        with open('configurations/results_fit_average.json', 'w') as fp:
            json.dump(results_avg, fp, indent=2)

    if False:
        with open('configurations/results_fit_average.json', 'r') as fp:
            results_avg = json.load(fp)
        fig = plt.figure(figsize=(10, 5))
        N = [8*i for i in range(10, 100, 10)]
        mu = [i / 10 for i in range(10 + 1)]
        # prefactor = lambda i: 1
        prefactor = lambda i: 1/(7*i)
        for m in mu:
            F_values = [prefactor(n) * results_avg[str(m)][str(n)][0] for n in N]
            F_stds = [prefactor(n) * results_avg[str(m)][str(n)][1] for n in N]
            plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', label=f"$\mu={m}$")
        plt.legend()
        plt.xticks(N)
        plt.title('$\\frac{1}{7N}$F(N) for different $\mu$ with $\\rho=0.3$')
        plt.xlabel('Number of bots')
        plt.ylabel('$\\frac{1}{7N}$F(N)')
        plt.grid()
        plt.savefig('F(N)div7N for different mu with rho=0.3.pdf')
        plt.show()

    if True:
        with open('configurations/results_isotropic_avg.json', 'r') as fp:
            results_avg = json.load(fp)
        fig = plt.figure(figsize=(10, 5))

        prefactor = lambda i: 1/(7*i)

        # N = [8, 16, 32, 64, 128]
        #
        # F_values = [prefactor(n) * results_avg[str(n)]['0.05'][0] for n in N]
        # F_stds = [prefactor(n) * results_avg[str(n)]['0.05'][1] for n in N]
        # plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.05}$ iso-bots")
        #
        # F_values = [prefactor(n) * results_avg[str(n)]['0.15'][0] for n in N]
        # F_stds = [prefactor(n) * results_avg[str(n)]['0.15'][1] for n in N]
        # plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.15}$ iso-bots")
        #
        # N = [64]
        #
        # F_values = [prefactor(n) * results_avg[str(n)]['0.3'][0] for n in N]
        # F_stds = [prefactor(n) * results_avg[str(n)]['0.3'][1] for n in N]
        # plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.3}$ iso-bots")
        #
        # F_values = [prefactor(n) * results_avg[str(n)]['0.4'][0] for n in N]
        # F_stds = [prefactor(n) * results_avg[str(n)]['0.4'][1] for n in N]
        # plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.4}$ iso-bots")
        #
        # F_values = [prefactor(n) * results_avg[str(n)]['0.5'][0] for n in N]
        # F_stds = [prefactor(n) * results_avg[str(n)]['0.5'][1] for n in N]
        # plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.5}$ iso-bots")

        with open('configurations/results_micelles_avg.json', 'r') as fp:
            results_avg = json.load(fp)

        N = [8, 16, 32, 64, 128]

        F_values = [prefactor(n) * results_avg[str(n//8)]['0.05'][0] for n in N]
        F_stds = [prefactor(n) * results_avg[str(n//8)]['0.05'][1] for n in N]
        plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.05}$ full micelles")

        F_values = [prefactor(n) * results_avg[str(n//8)]['0.25'][0] for n in N]
        F_stds = [prefactor(n) * results_avg[str(n//8)]['0.25'][1] for n in N]
        plt.errorbar(x=N, y=F_values, yerr=F_stds, fmt='o', capsize=5, label=f"$\\rho={0.25}$ full micelles")

        plt.xticks([8, 16, 32, 64, 128])
        plt.title('$\\frac{1}{7N}$F(N) for different configurations')
        plt.xlabel('Number of bots')
        plt.ylabel('$\\frac{1}{7N}$F(N)')
        plt.grid()
        plt.legend()
        plt.savefig('F(N)div7N for different configurations 2.pdf')
        plt.show()

    '''
    N = 100
    borders = ((-100, 100),
               (-80, 80))
    borders_angle = (-10, 10)
    config = Configuration()
    config.ClearConfiguration()
    for i in range(N):
        config.AddBotRandomized(borders_x = borders[0], borders_y=borders[1], borders_angle=borders_angle)
    config.SaveConfiguration(f'isotropic_oriented_N_{N}_D_{borders[0][1] - borders[0][0]}x{borders[1][1] - borders[1][0]}.npy')
    print(config.GetConfiguration())
    '''

    '''
    struct_half_micelle = np.load('half_micelle.npy', allow_pickle=True).tolist()
    N = 40
    borders = ((-90, 90),
               (-70, 70))
    borders_angle = (0, 360)
    config = Configuration()
    config.ClearConfiguration()
    for i in range(N):
        config.AddStructureRandomized(structure=struct_half_micelle, borders_x = borders[0], borders_y=borders[1], borders_angle=borders_angle, offset=2*BOT_LENGTH)
    config.SaveConfiguration(f'half_micelles_N_{N}_D_{borders[0][1] - borders[0][0]}x{borders[1][1] - borders[1][0]}.npy')
    print(config.GetConfiguration())
    '''

    # struct_micelle = np.load('micelle.npy', allow_pickle=True).tolist()
    # N_M = 1
    # N_B = 200
    # iterations = 10
    #
    # borders_M = ((-20, 20),
    #             (-20, 20))
    # borders_angle_M = (0, 360)
    #
    # borders_B = ((-100, 100),
    #             (-80, 80))
    # borders_angle_B = (0, 360)
    #
    # config = Configuration()
    #
    # for iter in range(iterations):
    #     config.ClearConfiguration()
    #     for i in range(N_M):
    #         config.AddStructureRandomized(structure=struct_micelle, borders_x=borders_M[0], borders_y=borders_M[1],
    #                                       borders_angle=borders_angle_M, offset=2 * BOT_LENGTH)
    #     for i in range(N_B):
    #         config.AddBotRandomized(borders_x = borders_B[0], borders_y=borders_B[1], borders_angle=borders_angle_B)
    #
    #     config.SaveConfiguration(f'configurations/micelle_in_crowd_N_{N_B}_iter_{iter+1}.npy')




    # config.LoadConfiguration('one_bot.npy')
    # config_list = [[1, 0, (-6.5, 0)]]
    # rotated_bots = config.RotateBotsAroundPoint(bots=config_list, angle=67.5)
    # print(rotated_bots)
    # config.ClearConfiguration()
    # config.AddBots(rotated_bots)
    # config.SaveConfiguration('mod.npy')






