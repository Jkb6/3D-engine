import pygame
import numpy as np
import math
import txt


pygame.init()

#DEFINIRANJE EKRANA
SCREEN_WIDTH = 256 * 4
SCREEN_HEIGHT = 240 * 4
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.update()

class vec3d:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

vCamera = vec3d()

class triangle:
    def __init__(self, v1 = vec3d(), v2 = vec3d, v3 = vec3d, color = (0, 0, 0)):
        self.p = [v1, v2, v3]
        self.color = color
        self.midpoint = 0
        


class matDef:
    def __init__(self, numOfRow, numOfCol, dtype):
        self.m = np.array([[0 for x in range(numOfCol)] for y in range(numOfRow)], dtype)

matProj = matDef(4, 4, float) #definiranje 4x4 matrice

class mesh:
    def __init__(self, fileName = None):
        
        self.tris = []
        self.vertexes = []
        self.faces = []
        
        if fileName == None:  
            return
        
        with open(fileName) as f:
            lines = f.readlines()
            
        verts = []
        tris = []
        for line in lines:
            if line[0] == "v":
                v = vec3d()
                
                line = line.split(" ")
                line.pop(0)
                line[2] =  line[2].replace(" \n", "")
                v.x = float(line[0])
                v.y = float(line[1])
                v.z = float(line[2])
                
                verts.append(v)
            if line[0] == "f":
                
                line = line.split(" ")
                line.pop(0)
                line[2] =  line[2].replace(" \n", "")
                
                f = triangle(verts[int(line[0]) - 1], verts[int(line[1]) - 1], verts[int(line[2]) - 1])
                self.tris.append(f)
                
        
        
meshCube = mesh("videoShip.txt")



fNear = 0.1
fFar = 1000
fFov = 90.0
fAspectRatio = SCREEN_HEIGHT/SCREEN_WIDTH
fFovRad = 1.0 / math.tan(fFov * 0.5 / 180 * math.pi)

# DEFINIRANJE PROJEKCIJSKE MATRICE
matProj.m[0][0] = fAspectRatio * fFovRad
matProj.m[1][1] = fFovRad
matProj.m[2][2] = fFar / (fFar - fNear)
matProj.m[3][2] = (-fFar * fNear) / (fFar - fNear)
matProj.m[2][3] = 1
matProj.m[3][3] = 0

# Z-ROTACIJSKA MATRICA


def MultiplyMatrixVector(i, m):
    o = vec3d(0, 0, 0)
    o.x = i.x * m.m[0][0] + i.y * m.m[1][0] + i.z * m.m[2][0] + m.m[3][0]
    o.y = i.x * m.m[0][1] + i.y * m.m[1][1] + i.z * m.m[2][1] + m.m[3][1]
    o.z = i.x * m.m[0][2] + i.y * m.m[1][2] + i.z * m.m[2][2] + m.m[3][2]
    w = i.x * m.m[0][3] + i.y * m.m[1][3] + i.z * m.m[2][3] + m.m[3][3]
    
    if w != 0:
        o.x /= w
        o.y /= w
        o.z /= w
    
    return o

def DrawTriangle(x1, y1, x2, y2, x3, y3, color):
    
    pygame.draw.line(screen, (0,0,0), (x1, y1), (x2,y2), 1)
    pygame.draw.line(screen, (0,0,0), (x1, y1), (x3,y3), 1)
    pygame.draw.line(screen, (0,0,0), (x3, y3), (x2,y2), 1)
    
    pygame.draw.polygon(screen, color, ((x1, y1), (x2,y2), (x3,y3)))
    
def GetColor(lum, bottomCol, topCol): #vrne barvno med vnošenima barvama glede na skalo med 0 in 1
    if lum < 0:
        lum = 0
    
    multiplR = abs(bottomCol[0] - topCol[0])
    multiplG = abs(bottomCol[1] - topCol[2])
    multiplB = abs(bottomCol[2] - topCol[2])
    return (lum * multiplR, lum * multiplG, lum * multiplB)
    

running = True
tPrev = 0
fTheta = 0
clock = pygame.time.Clock()

while running:
    deltaTime = pygame.time.get_ticks() - tPrev
    tPrev = pygame.time.get_ticks()
    
    clock.tick(60)
    pygame.display.set_caption("FPS: " + str(int(clock.get_fps())))
    
    screen.fill((0,0,0,255))
    
    fTheta += deltaTime * 0.001 #pretvorba časa v sekunde(iz milisekund)
    
    # Z-ROTACIJSKA MATRICA
    matRotZ = matDef(4, 4, float)
    matRotZ.m[0][0] = math.cos(fTheta)
    matRotZ.m[0][1] = math.sin(fTheta)
    matRotZ.m[1][0] = -math.sin(fTheta)
    matRotZ.m[1][1] = math.cos(fTheta)
    matRotZ.m[2][2] = 1
    matRotZ.m[3][3] = 1
    
    # X-ROTACIJSKA MATRICA
    matRotX = matDef(4, 4, float)
    matRotX.m[0][0] = 1
    matRotX.m[1][1] = math.cos(fTheta * 0.5)
    matRotX.m[1][2] = math.sin(fTheta * 0.5)
    matRotX.m[2][1] = -math.sin(fTheta * 0.5)
    matRotX.m[2][2] = math.cos(fTheta * 0.5)
    matRotX.m[3][3] = 1
    
    
    # Risanje Trikotnikov
    vecTrianglesToRaster = []
    
    i = 0
    for tri in meshCube.tris:
        triProjected = triangle(vec3d(0, 0, 0), vec3d(0, 0, 0,), vec3d(0, 0, 0,))
        
        #ROTACIJA KOCKE NA Z
        triRotatedZ = triangle(vec3d(0, 0, 0), vec3d(0, 0, 0,), vec3d(0, 0, 0,))
        triRotatedZ.p[0] = MultiplyMatrixVector(tri.p[0], matRotZ)
        triRotatedZ.p[1] = MultiplyMatrixVector(tri.p[1], matRotZ)
        triRotatedZ.p[2] = MultiplyMatrixVector(tri.p[2], matRotZ)
        
        #ROTACIJA KOCKE NA X
        triRotatedZX = triangle(vec3d(0, 0, 0), vec3d(0, 0, 0,), vec3d(0, 0, 0,))
        triRotatedZX.p[0] = MultiplyMatrixVector(triRotatedZ.p[0], matRotX)
        triRotatedZX.p[1] = MultiplyMatrixVector(triRotatedZ.p[1], matRotX)
        triRotatedZX.p[2] = MultiplyMatrixVector(triRotatedZ.p[2], matRotX)
        
        #ZAMIK NA EKRAN
        triTranslated = triangle(vec3d(triRotatedZX.p[0].x, triRotatedZX.p[0].y, triRotatedZX.p[0].z + 10),
                         vec3d(triRotatedZX.p[1].x, triRotatedZX.p[1].y, triRotatedZX.p[1].z + 10),
                         vec3d(triRotatedZX.p[2].x, triRotatedZX.p[2].y, triRotatedZX.p[2].z + 10))

        normal = vec3d(0, 0, 0)
        line1 = vec3d(0, 0, 0)
        line2 = vec3d(0, 0, 0)
        
        
        line1.x = triTranslated.p[1].x - triTranslated.p[0].x
        line1.y = triTranslated.p[1].y - triTranslated.p[0].y
        line1.z = triTranslated.p[1].z - triTranslated.p[0].z
        
        line2.x = triTranslated.p[2].x - triTranslated.p[0].x
        line2.y = triTranslated.p[2].y - triTranslated.p[0].y
        line2.z = triTranslated.p[2].z - triTranslated.p[0].z

        
        normal.x = line1.y * line2.z - line1.z * line2.y
        normal.y = line1.z * line2.x - line1.x * line2.z
        normal.z = line1.x * line2.y - line1.y * line2.x
        
        lenght = math.sqrt(normal.x*normal.x + normal.y*normal.y + normal.z*normal.z)
        
        if lenght == 0:
            print(i)
        i += 1
        
        normal.x /= lenght
        normal.y /= lenght
        normal.z /= lenght
 
        # naslednji del kode se izvede le, če lahko vidimo trikotnik
        if (normal.x * (triTranslated.p[0].x - vCamera.x) +
            normal.y * (triTranslated.p[0].y - vCamera.y) +
            normal.z * (triTranslated.p[0].z - vCamera.z)) < 0:
            
            light_direction = vec3d(0, 0, -1)
            lenght = math.sqrt(light_direction.x*light_direction.x + light_direction.y*light_direction.y 
                               + light_direction.z*light_direction.z)
            light_direction.x /= lenght
            light_direction.y /= lenght
            light_direction.z /= lenght
            
            
            #podobnost(dot product) med normalo ploskve(pravokoten vektor) in smerjo 
            #svetlone(ki sicer kaže proti igralcu za lažji račun)
            dp = normal.x*light_direction.x + normal.y*light_direction.y + normal.z*light_direction.z 
            
            triProjected.color = GetColor(dp, (0, 0, 0), (255,255,255))
            
            #PROJEKCIJA 3D --> 2D
            triProjected.p[0] = MultiplyMatrixVector(triTranslated.p[0], matProj)
            triProjected.p[1] = MultiplyMatrixVector(triTranslated.p[1], matProj)
            triProjected.p[2] = MultiplyMatrixVector(triTranslated.p[2], matProj)
            
            
            # Povečava in premik na enkranu
            triProjected.p[0].x += 1
            triProjected.p[0].y += 1
            triProjected.p[1].x += 1
            triProjected.p[1].y += 1
            triProjected.p[2].x += 1
            triProjected.p[2].y += 1
            
            triProjected.p[0].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[0].y *= 0.5 * SCREEN_HEIGHT
            triProjected.p[1].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[1].y *= 0.5 * SCREEN_HEIGHT
            triProjected.p[2].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[2].y *= 0.5 * SCREEN_HEIGHT
            
            #Risanje trikotnikov, ki niso pokriti
            triProjected.midpoint = (triProjected.p[0].z + triProjected.p[1].z + triProjected.p[2].z) / 3
            vecTrianglesToRaster.append(triProjected) 
            
            
        
        
        newList = sorted(vecTrianglesToRaster, key=lambda trik: -trik.midpoint) #tam je minus ker želim, da sortira od največjega do najmanjšega
        
        for triProjected in newList:
            DrawTriangle(triProjected.p[0].x, triProjected.p[0].y, triProjected.p[1].x, triProjected.p[1].y, triProjected.p[2].x, triProjected.p[2].y, triProjected.color)    
    
    pygame.display.update()
    
    for event in pygame.event.get():
        if event == pygame.QUIT:
            running = False

pygame.quit()