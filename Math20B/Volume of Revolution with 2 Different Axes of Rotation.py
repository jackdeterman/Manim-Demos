from manim import *

class VORDemo(ThreeDScene):
    def construct(self):
        self.camera.background_color = WHITE

        def outerfunc(x):
            return x

        def innerfunc(x):
            return x**2

        skip = False
        axes = ThreeDAxes(x_range=[-0.5, 1.5], y_range=[-3.5, 1.5], z_range=[-2.5, 2.5],
                  tips=False, x_length=6, y_length=7, axis_config={"color": BLACK})
        outer = axes.plot_parametric_curve(lambda t: [t, outerfunc(t), 0], t_range=[0, 1, 0.05], color=PURE_BLUE)
        inner = axes.plot_parametric_curve(lambda t: [t, innerfunc(t), 0], t_range=[0, 1, 0.05], color=PURE_RED)
        x = 0.6  # x location of segment
        segment = Line(axes.c2p(x,innerfunc(x),0),axes.c2p(x,outerfunc(x),0), color=BLACK)
        AOR = DashedLine(axes.c2p(-1, 0, 0), axes.c2p(2, 0, 0), color=DARK_BROWN)
        AORlabel = always_redraw(lambda: Tex(r"Axis of\\revolution", font_size=28, color=DARK_BROWN).next_to(AOR,0.5*LEFT))
        outerlabel = Tex(r"$y=x$",font_size=28,color=PURE_BLUE
                         ).move_to(axes.c2p(1,1.5,0))
        innerlabel = Tex(r"$y=x^2$", font_size=28, color=PURE_RED).move_to(axes.c2p(1, 0.5, 0))

        # set the stage
        self.next_section(skip_animations=skip)
        self.play(Succession(Create(axes),
                             FadeIn(inner,innerlabel),
                             FadeIn(outer,outerlabel),
                             Create(segment),
                             FadeIn(AOR,AORlabel)))
        self.wait(1)

        # move to 3D view
        self.next_section(skip_animations=skip)
        self.move_camera(phi=60*DEGREES, theta=-45*DEGREES, run_time=2)

        #Added legend to graph in 3-D view to supplement readability
        legend_items = VGroup(
        Dot(color=PURE_BLUE).scale(0.5), Tex(r"$y=x$", font_size=24, color=PURE_BLUE),
        Dot(color=PURE_RED).scale(0.5), Tex(r"$y=x^2$", font_size=24, color=PURE_RED),
        Dot(color=DARK_BROWN).scale(0.5), Tex(r"Axis of Revolution", font_size=24, color=DARK_BROWN)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        legend_items.next_to(axes, UP + RIGHT, buff=1).shift(DOWN*2)

        legend_box = SurroundingRectangle(legend_items, color=GRAY, buff=0.1)
        legend = VGroup(legend_items, legend_box)

        self.add_fixed_in_frame_mobjects(legend)  # This keeps the legend static in the frame
        self.add(legend)
        #End of legend code (In case it's trash and needs to be disposed of)

        inner_radius_line = DashedLine(AOR.get_center(), axes.c2p(x, innerfunc(x), 0), color=PURE_RED)
        outer_radius_line = DashedLine(AOR.get_center(), axes.c2p(x, outerfunc(x), 0), color=PURE_BLUE)
        inner_radius_label = Tex("Inner Radius", font_size=24, color=BLACK).next_to(inner_radius_line, DOWN, buff=0.1)
        outer_radius_label = Tex("Outer Radius", font_size=24, color=BLACK).next_to(outer_radius_line, UP, buff=0.1).shift(UP*0.5)

        self.play(Create(inner_radius_line), Write(inner_radius_label))
        self.wait(2)
        self.play(FadeOut(inner_radius_line), FadeOut(inner_radius_label))
        self.play(Create(outer_radius_line), Write(outer_radius_label))
        self.wait(2)
        self.play(FadeOut(outer_radius_line), FadeOut(outer_radius_label))

        # first revolution: no trace
        self.next_section(skip_animations=skip)
        graphgrp = VGroup(outer,inner,segment)
        self.play(Rotating(graphgrp, axis=RIGHT, about_point=axes.c2p(0,0,0), angle=2*PI), run_time=3)
        self.wait(1)

        # second revolution: show washer
        self.next_section(skip_animations=skip)
        outerpath = TracedPath(segment.get_end, stroke_color=ManimColor('#000000'))
        innerpath = TracedPath(segment.get_start, stroke_color=ManimColor('#000000'))
        self.add(outerpath, innerpath)
        self.play(Rotating(graphgrp, axis=RIGHT, about_point=axes.c2p(0,0,0), angle=2*PI), run_time=3)
        self.play(FadeOut(outerpath,innerpath))

        #########################################################
        # helper functions for movement of washers along x axis #
        #########################################################
        # function draws a parametric circle in y/z plane to func(xval) from y = AOR aor, at x = xval, in color
        def getCircle(func, xval, color, aor):
            return ParametricFunction(lambda t: axes.c2p(xval,
                                                         (func(xval)-aor)*np.cos(t)+aor,
                                                         (func(xval)-aor)*np.sin(t)
                                                         ),
                                      t_range = [0,2*PI,0.1],
                                      color=color)

        def xMovement(aor, tempo=1):
            xval = ValueTracker(x)
            outerring = always_redraw(lambda: getCircle(outerfunc, xval.get_value(), PURE_BLUE, aor))
            innerring = always_redraw(lambda: getCircle(innerfunc, xval.get_value(), PURE_RED, aor))
            self.play(FadeIn(outerring, innerring))
            self.play(xval.animate.set_value(0), run_time=tempo)
            self.play(xval.animate.set_value(1), run_time=2*tempo)
            self.play(xval.animate.set_value(x), run_time=tempo)
            self.play(FadeOut(outerring, innerring))

        # End helper functions

        self.next_section(skip_animations=skip)
        xMovement(0,2)

        ################################################
        # helper functions to return and draw surfaces #
        ################################################

        def getSurface(func,opacity,color,resolution,aor):
            return Surface(lambda u,v: axes.c2p(u,(func(u)-aor)*np.cos(v)+aor,(func(u)-aor)*np.sin(v)),
                           u_range=[0,1], v_range=[0,2*PI],
                           resolution=resolution,
                           checkerboard_colors=[BLACK,color],
                           fill_opacity=opacity)

        def surfaceViz(aor):
            innersurf = getSurface(innerfunc,1,PURE_RED,10,aor)
            outersurf = getSurface(outerfunc,0.3,PURE_BLUE,10,aor)
            self.play(FadeIn(innersurf))
            self.wait()
            self.play(FadeIn(outersurf))
            self.wait()
            self.begin_ambient_camera_rotation(-PI/4)
            self.wait(2)
            self.stop_ambient_camera_rotation()
            self.wait()
            self.begin_ambient_camera_rotation(PI/4)
            self.wait(2)
            self.stop_ambient_camera_rotation()
            self.play(Rotating(graphgrp, axis=RIGHT, about_point=axes.c2p(0,aor,0), angle=2*PI), run_time=3)
            self.play(FadeOut(innersurf,outersurf))

        # End surface helper functions

        # first surface viz
        self.next_section(skip_animations=skip)
        surfaceViz(0)

        # shift AOR
        self.next_section(skip_animations=skip)
        newAOR = DashedLine(axes.c2p(-1,-1,0),axes.c2p(2,-1,0), color=DARK_BROWN)
        self.play(ReplacementTransform(AOR,newAOR))

        new_inner_radius_line = DashedLine(AOR.get_center(), axes.c2p(x, innerfunc(x), 0), color=PURE_RED)
        new_outer_radius_line = DashedLine(AOR.get_center(), axes.c2p(x, outerfunc(x), 0), color=PURE_BLUE)

        self.play(Create(new_inner_radius_line), Write(inner_radius_label))
        self.wait(2)
        self.play(FadeOut(new_inner_radius_line), FadeOut(inner_radius_label))
        self.play(Create(new_outer_radius_line), Write(outer_radius_label))
        self.wait(2)
        self.play(FadeOut(new_outer_radius_line), FadeOut(outer_radius_label))

        # third revolution: show larger washer
        newouterpath = TracedPath(segment.get_end, stroke_color=ManimColor('#000000'))
        newinnerpath = TracedPath(segment.get_start, stroke_color=ManimColor('#000000'))
        self.add(newouterpath, newinnerpath)
        self.next_section(skip_animations=skip)
        self.play(Rotating(graphgrp, axis=RIGHT, about_point=axes.c2p(0, -1, 0), angle=2*PI), run_time=3)
        self.play(FadeOut(newouterpath,newinnerpath))

        # second x movement (with larger washer)
        self.next_section(skip_animations=skip)
        xMovement(-1,2)
        self.wait(2)

        # second surface viz
        self.next_section(skip_animations=skip)
        surfaceViz(-1)
