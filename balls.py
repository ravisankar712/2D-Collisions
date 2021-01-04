from manimlib.imports import *

class Ball(VGroup):
    CONFIG = {
        "col" : GREEN,
        "r" : 0.1,
        "m" : 2.0,
        "max_speed" : 2.0
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = np.random.uniform(-self.max_speed, self.max_speed, size=3)
        self.velocity[2] = 0.0
        # self.acceleration = np.zeros(3)
        self.create_body()
        self.balls = []
        self.walls = []
        self.add_updater(lambda m, dt: m.move(dt))

    def create_body(self):
        body = Circle(color=self.col, radius=self.r, fill_opacity=1.0)
        body.move_to(self.get_center())
        self.body = body
        self.add(self.body)

    def change_velocity(self, vel):
        self.velocity = vel

    def check_walls(self):
        for w in self.walls:
            pos = self.get_center()
            w_pos = w.get_center()
            r = self.r
            if pos[0] > w_pos[0]:
                if w.get_top()[1] > pos[1] > w.get_bottom()[1]:
                    if pos[0] - r < w.get_right()[0]:
                        self.velocity[0] *= -1
                        self.move_to(np.array([w.get_right()[0] + r, pos[1], 0.0]))
            else:
                if w.get_top()[1] > pos[1] > w.get_bottom()[1]:
                    if pos[0] + r > w.get_left()[0]:
                        self.velocity[0] *= -1
                        self.move_to(np.array([w.get_left()[0] - r, pos[1], 0.0]))
            if pos[1] > w_pos[1]:
                if w.get_right()[0] > pos[0] > w.get_left()[0]:
                    if pos[1] - r < w.get_top()[1]:
                        self.velocity[1] *= -1
                        self.move_to(np.array([pos[0], w.get_top()[1] + r, 0.0]))
            else:
                if w.get_right()[0] > pos[0] > w.get_left()[0]:
                    if pos[1] + r > w.get_bottom()[1]:
                        self.velocity[1] *= -1
                        self.move_to(np.array([pos[0], w.get_bottom()[1] - r, 0.0]))



    def check_edges(self):
        pos = self.get_center()
        r = self.r
        if pos[0] - r < -FRAME_X_RADIUS:
            # self.shift(r * RIGHT)
            self.velocity[0] *= -1
            self.move_to(np.array([-FRAME_X_RADIUS + r, pos[1], 0.0]))
        if pos[0] + r > FRAME_X_RADIUS:
            # self.shift(r * LEFT)
            self.velocity[0] *= -1
            self.move_to(np.array([FRAME_X_RADIUS - r, pos[1], 0.0]))
        if pos[1] + r > FRAME_Y_RADIUS:
            # self.shift(r * DOWN)
            self.velocity[1] *= -1
            self.move_to(np.array([pos[0], FRAME_Y_RADIUS - r, 0.0]))
        if pos[1] - r < -FRAME_Y_RADIUS:
            # self.shift(r * UP)
            self.velocity[1] *= -1
            self.move_to(np.array([pos[0], -FRAME_Y_RADIUS + r, 0.0]))

    def move(self, dt):
        self.check_edges()
        self.check_walls()
        
        speed = np.linalg.norm(self.velocity)
        # if speed > self.max_speed:
        #     self.velocity /= speed
        self.shift(self.velocity * dt)

class Simulation(VGroup):
    CONFIG = {
        "num_particles" : 10,
        "particle_r" : 0.2,
        "wall_list" : []
    }

    def __init__(self, mixed=False, **kwargs):
        super().__init__(**kwargs)
        self.mixed = mixed
        self.create_particles()
        self.add_updater(lambda m, dt: m.collisions(dt))

    def create_particles(self):
        bs = []
        for _ in range(self.num_particles):
            count = 0
            while True and count < 1000:
                got_pos = True
                x = random.uniform(-FRAME_X_RADIUS, FRAME_X_RADIUS)
                y = random.uniform(-FRAME_Y_RADIUS, FRAME_Y_RADIUS)
                for bb in bs:
                    if np.linalg.norm(bb.get_center() - np.array([x, y, 0.0])) > 2.5*self.particle_r:
                        got_pos *= True
                if got_pos:
                    break
                else: count += 1
            if not self.mixed:
                if x < 0.0:
                    b = Ball(col="#caf0f8", r=self.particle_r)
                else:
                    b = Ball(col="#00b4d8", r=self.particle_r)
            else:
                b = Ball(col=random.choice(["#caf0f8", "#00b4d8"]), r=self.particle_r)
            b.walls = self.wall_list
            bs.append(b.shift(np.array([x, y ,0])))
        self.particles = bs
        self.add(*bs, *self.wall_list)

    def handle_collisions(self, p1, p2):
        r1 = p1.r 
        r2 = p2.r
        m1 = p1.m
        m2 = p2.m 
        v1 = p1.velocity
        v2 = p2.velocity
        x1 = p1.get_center()
        x2 = p2.get_center()
        d = np.linalg.norm(x1-x2)**2
        if (r1+r2)**2 > d:
            u1 = v1 - 2*m2/(m1+m2) * np.dot(v1-v2, x1-x2)/d * (x1-x2)
            u2 = v2 - 2*m1/(m1+m2) * np.dot(v2-v1, x2-x1)/d * (x2-x1)
            p1.change_velocity(u1)
            p2.change_velocity(u2)
        else:
            pass
    
    def collisions(self, dt):
        for i in range(len(self.particles)):
            for j in range(i+1, len(self.particles)):
                self.handle_collisions(self.particles[i], self.particles[j])


class Test(Scene):
    CONFIG = {
        "random_seed" : None
    }
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        w5 = Rectangle(width=0.05, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY)
        s = Simulation(num_particles=800, mixed=False, particle_r=0.05, wall_list=[w1, w2, w3, w4, w5])
        self.add(s)
        self.wait(1)
        # self.play(
        #     ApplyMethod(w5.shift, UP*(FRAME_X_RADIUS + 1))
        # )
        # self.wait(20)

class Water_Mixing(Scene):
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        w5 = Rectangle(width=0.05, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY)
        s = Simulation(num_particles=800, mixed=False, particle_r=0.05, wall_list=[w1, w2, w3, w4, w5])
        self.add(s)
        self.wait(7)
        self.play(
            ApplyMethod(w5.shift, UP*(FRAME_X_RADIUS + 1))
        )
        self.wait(35)

class MixedUp(Scene):
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        s = Simulation(num_particles=250, mixed=True, particle_r=0.1, wall_list=[w1, w2, w3, w4])
        self.add(s)
        self.wait(20)

class Four_Balls(Scene):
    CONFIG = {
        "random_seed" : 1
    }
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        w5 = Rectangle(width=0.05, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY)
        s = Simulation(num_particles=8, mixed=False, particle_r=0.1, wall_list=[w1, w2, w3, w4, w5])
        self.add(s)
        self.wait(5)
        self.play(
            ApplyMethod(w5.shift, UP*(FRAME_X_RADIUS + 1))
        )
        self.wait(15)

class TwentyFive_Balls(Scene):
    CONFIG = {
        "random_seed" : 1
    }
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        w5 = Rectangle(width=0.05, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY)
        s = Simulation(num_particles=50, mixed=False, particle_r=0.1, wall_list=[w1, w2, w3, w4, w5])
        self.add(s)
        self.wait(5)
        self.play(
            ApplyMethod(w5.shift, UP*(FRAME_X_RADIUS + 1))
        )
        self.wait(15)

class TwoBalls(Scene):
    CONFIG = {
        "random_seed" : 1
    }
    def construct(self):
        w1 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(LEFT, buff=0.0)
        w2 = Rectangle(width=0.2, height=FRAME_HEIGHT, fill_opacity=1.0, color=GREY).to_edge(RIGHT, buff=0.0)
        w3 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(UP, buff=0.0)
        w4 = Rectangle(width=FRAME_WIDTH, height=0.2, fill_opacity=1.0, color=GREY).to_edge(DOWN, buff=0.0)
        s = Simulation(num_particles=2, mixed=True, particle_r=0.2, wall_list=[w1, w2, w3, w4])
        s.particles[0].to_corner(UL)
        s.particles[0].change_velocity(np.array([FRAME_X_RADIUS/2, -FRAME_Y_RADIUS/2 + 0.5, 0.0]))
        s.particles[1].to_corner(DR)
        s.particles[1].change_velocity(np.array([-FRAME_X_RADIUS/2, FRAME_Y_RADIUS/2, 0.0]))
        self.add(s)

        self.wait(5)


