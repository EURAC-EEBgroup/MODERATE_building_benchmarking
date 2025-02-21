import dash_mantine_components as dmc
from dash import get_relative_path

Footer = dmc.AppShellFooter(
    h=200,
    pt=20,
    children = [
        dmc.Container(
            size="md",
            children= [
                dmc.Group(
                    children = [
                        dmc.Stack(
                            children = [
                                dmc.Avatar(
                                    src=get_relative_path("/assets/moderate_logo.png"), radius=0,
                                    style ={
                                        'width':'70%',
                                        'height': '60px',
                                        # 'mar':'3px'
                                    }
                                ),
                                dmc.Text(
                                    children = [
                                        "Horizon Europe research and innovation programme under grant agreement No 101069834. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or CINEA. Neither the European Union nor the granting authority can be held responsible for."
                                    ],
                                    size="12px",
                                    mt=5,
                                    
                                    style = {
                                        'color':'rgb(134, 142, 150)',
                                        'lineHeight':'1.55'    
                                    }
                                )
                            ],
                            style = {'maxWidth':'380px'}
                        ),
                        dmc.Stack(
                            children = [
                                dmc.Text("About MODERATE", size="18px", fw=800, mb=10, mt=0),
                                dmc.Anchor(
                                    children = dmc.Text("In a nutshell", c='rgb(134, 142, 150)',size='14px', pt=3, pb=3, fw=500),
                                    href="https://moderate-project.eu/in-a-nutshell/"
                                ),
                                dmc.Anchor(
                                    children = dmc.Text("News", c='rgb(134, 142, 150)',size='14px', pt=3, pb=3, fw=500),
                                    href="https://moderate-project.eu/news/"
                                ),
                                dmc.Anchor(
                                    children = dmc.Text("Contact",c='rgb(134, 142, 150)',size='14px', pt=3, pb=3, fw=500),
                                    href="https://moderate-project.eu/contact/"
                                ),
                            ],
                            gap="6px"
                        )
                    ],
                    justify="space-between",
                    align="top"
                )
            ]
        )
    ]
)