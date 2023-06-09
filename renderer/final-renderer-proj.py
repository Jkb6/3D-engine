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
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(1)

vCamera = vec3d()

class triangle:
    def __init__(self, v1 = vec3d(), v2 = vec3d, v3 = vec3d, color = (0, 0, 0)):
        self.p = [v1, v2, v3]
        self.color = color
        self.midpoint = 0
        


class matDef:
    def __init__(self, numOfRow, numOfCol, dtype):
        self.m = np.array([[0 for x in range(numOfCol)] for y in range(numOfRow)], dtype)


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


def Matrix_MulitplyVector(matrix, vec):
    v = vec3d()
    v.x = vec.x * matrix.m[0][0] + vec.y * matrix.m[1][0] + vec.z * matrix.m[2][0] + vec.w * matrix.m[3][0]
    v.y = vec.x * matrix.m[0][1] + vec.y * matrix.m[1][1] + vec.z * matrix.m[2][1] + vec.w * matrix.m[3][1]
    v.z = vec.x * matrix.m[0][2] + vec.y * matrix.m[1][2] + vec.z * matrix.m[2][2] + vec.w * matrix.m[3][2]
    v.w = vec.x * matrix.m[0][3] + vec.y * matrix.m[1][3] + vec.z * matrix.m[2][3] + vec.w * matrix.m[3][3]
    return v

def Matrix_Makeidentity():
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = 1
    matrix.m[1][1] = 1
    matrix.m[2][2] = 1
    matrix.m[3][3] = 1
    return matrix

def Matrix_MakeRotationX(fAngleRad):
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = 1
    matrix.m[1][1] = math.cos(fAngleRad)
    matrix.m[1][2] = math.sin(fAngleRad)
    matrix.m[2][1] = -math.sin(fAngleRad)
    matrix.m[2][2] = math.cos(fAngleRad)
    matrix.m[3][3] = 1
    return matrix

def Matrix_MakeRotationY(fAngleRad):
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = math.cos(fAngleRad)
    matrix.m[0][2] = math.sin(fAngleRad)
    matrix.m[2][0] = -math.sin(fAngleRad)
    matrix.m[1][1] = 1
    matrix.m[2][2] = math.cos(fAngleRad)
    matrix.m[3][3] = 1
    return matrix

def Matrix_MakeRotationZ(fAngleRad):
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = math.cos(fAngleRad)
    matrix.m[0][1] = math.sin(fAngleRad)
    matrix.m[1][0] = -math.sin(fAngleRad)
    matrix.m[1][1] = math.cos(fAngleRad)
    matrix.m[2][2] = 1.0
    matrix.m[3][3] = 1.0
    return matrix

def Matrix_MakeTranslation(x, y, z):
    matrix = Matrix_Makeidentity()
    matrix.m[3][0] = x
    matrix.m[3][1] = y
    matrix.m[3][2] = z
    print(matrix.m)
    return matrix

def Matrix_MakeProjection(fFovDegrees, fAspectRatio, fNear, fFar):
    fFovRad = 1 / math.tan(fFovDegrees * 0.5 / 180 * math.pi)
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = fAspectRatio * fFovRad
    matrix.m[1][1] = fFovRad
    matrix.m[2][2] = fFar / (fFar - fNear)
    matrix.m[3][2] = (-fFar * fNear) / (fFar - fNear)
    matrix.m[2][3] = 1
    matrix.m[3][3] = 0
    return matrix
    
def Matrix_MultiplyMatrix(m1, m2):
    matrix = matDef(4, 4, float)
    for c in range(4):
        for r in range(4):
            matrix.m[r][c] = m1.m[r][0] * m2.m[0][c] + m1.m[r][1] * m2.m[1][c] + m1.m[r][2] * m2.m[2][c] + m1.m[r][3] * m2.m[3][c]
    return matrix

def Matrix_PointAt(pos, target, up):
    #NOVA SMER NAPREJ
    newForward = Vector_Sub(target, pos)
    newForward = Vector_Normalise(newForward)
    
    #NOVA SMER GOR
    a = Vector_Mul(newForward, Vector_DotProduct(up, newForward))
    newUp = Vector_Sub(up, a)
    newUp = Vector_Normalise(newUp)
        
    #NOVA SMER DESNO
    newRight = Vector_CrossProduct(newUp, newForward)
    
    matrix = matDef(4, 4, float)
    matrix.m[0][0] = float(newRight.x)
    matrix.m[1][0] = float(newUp.x)
    matrix.m[2][0] = float(newForward.x)
    matrix.m[3][0] = float(pos.x)
    
    matrix.m[0][1] = float(newRight.y)
    matrix.m[1][1] = float(newUp.y)
    matrix.m[2][1] = float(newForward.y)
    matrix.m[3][1] = float(pos.y)
    
    matrix.m[0][2] = float(newRight.z)
    matrix.m[1][2] = float(newUp.z)
    matrix.m[2][2] = float(newForward.z)
    matrix.m[3][2] = float(pos.z)
    
    matrix.m[0][3] = 0.0
    matrix.m[1][3] = 0.0
    matrix.m[2][3] = 0.0
    matrix.m[3][3] = 1.0
        
    return matrix

def Matrix_QuickInverse(m):
    return np.linalg.inv(m.m)
    
def Vector_Add(v1, v2):
    return vec3d(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def Vector_Sub(v1, v2):
    return vec3d(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def Vector_Mul(v1, k):
    return vec3d(v1.x * k, v1.y * k, v1.z * k)

def Vector_Div(v1, k):
    return vec3d(v1.x / k, v1.y / k, v1.z / k)

def Vector_DotProduct(v1, v2):
    return float(v1.x * v2.x + v1.y * v2.y + v1.z * v2.z)

def Vector_Lenght(v):
    return float(math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z))

def Vector_Normalise(v):
    l = Vector_Lenght(v)
    if l == 0:
        return vec3d(0, 0, 0)
    return vec3d(v.x / l, v.y / l, v.z / l)

def Vector_CrossProduct(v1, v2):
    v = vec3d()
    v.x = v1.y * v2.z - v1.z * v2.y
    v.y = v1.z * v2.x - v1.x * v2.z
    v.z = v1.x * v2.y - v1.y * v2.x
    return v

def DrawTriangle(x1, y1, x2, y2, x3, y3, color, drawEdge = False):
    
    if drawEdge:
        pygame.draw.line(screen, (255,0,0), (x1, y1), (x2,y2), 2)
        pygame.draw.line(screen, (255,0,0), (x1, y1), (x3,y3), 2)
        pygame.draw.line(screen, (255,0,0), (x3, y3), (x2,y2), 2)
    
    pygame.draw.polygon(screen, color, ((x1, y1), (x2,y2), (x3,y3)))
    
def GetColor(lum, bottomCol, topCol, bias = 1): #vrne barvno med vnošenima barvama glede na skalo med -1 in 1
    lum += 1
    lum /= 2
    
    multiplR = lum * abs(bottomCol[0] - topCol[0])
    multiplG = lum * abs(bottomCol[1] - topCol[2])
    multiplB = lum * abs(bottomCol[2] - topCol[2])
    
    #if multiplR != 255 and multiplB != 255 and multiplG != 255:
    #    multiplR = (1-(1 - multiplR / 255) / bias) *255
    #    multiplG = (1-(1 - multiplG / 255) / bias) *255
    #    multiplB = (1-(1 - multiplB / 255) / bias) *255
    return (multiplR, multiplG, multiplB)
    


# DEFINIRANJE PROJEKCIJSKE MATRICE
matProj = Matrix_MakeProjection(90, SCREEN_HEIGHT / SCREEN_WIDTH, 0.1, 1000)



running = True
tPrev = 0
fTheta = 0
clock = pygame.time.Clock()

vCamera = vec3d(0, 0, 0)

Krej = matDef(4, 4, float)
Krej = Matrix_MakeTranslation(0, 0, 10)

Zi = vec3d()
Zi = Matrix_MulitplyVector(Krej, Zi)

print(Zi.x)
print(Zi.y)
print(Zi.z)
print(Zi.w)


while running:
    deltaTime = pygame.time.get_ticks() - tPrev
    tPrev = pygame.time.get_ticks()
    
    pressed_keys = pygame.key.get_pressed()
    
    clock.tick(60)
    pygame.display.set_caption("FPS: " + str(int(clock.get_fps())))
    
    screen.fill((0,0,0))
    
    fTheta += deltaTime * 0.001 #pretvorba časa v sekunde(iz milisekund)
    
    # Z-ROTACIJSKA MATRICA
    matRotZ = matDef(4, 4, float)
    matRotZ = Matrix_MakeRotationZ(fTheta * 0.5)
    
    # X-ROTACIJSKA MATRICA
    matRotX = matDef(4, 4, float)
    matRotX = Matrix_MakeRotationY(fTheta)
    
    matTrans = matDef(4, 4, float)
    matTrans = Matrix_MakeTranslation(0, 0, 10)
    
    matWorld = matDef(4, 4, float)
    matWorld = Matrix_Makeidentity()
    #matWorld = Matrix_MultiplyMatrix(matRotZ, matRotX)
    #matWorld = Matrix_MultiplyMatrix(matWorld, matTrans)
    
    vCamera = vec3d(0, 0, -15)
    vLookDirection = vec3d(0, 0, 1)
    vUp = vec3d(0, 1, 0)
    vTarget = Vector_Add(vCamera, vLookDirection)
    
    matCamera = Matrix_PointAt(vCamera, vTarget, vUp)
    
    matView = matDef(4,4, float)
    matView.m = Matrix_QuickInverse(matCamera)
    
    # Risanje Trikotnikov
    vecTrianglesToRaster = []
    
    vCamera.y += 1
    
    for tri in meshCube.tris:
        triProjected = triangle()
        triTransformed = triangle()
        triViewed = triangle()
        
        for i in range(3):
            triTransformed.p[i] = Matrix_MulitplyVector(matWorld, tri.p[i])

        #RAČUNANJE NORMALE
        normal = vec3d()
        line1 = vec3d()
        line2 = vec3d()
        
        
        line1 = Vector_Sub(triTransformed.p[1], triTransformed.p[0])
        
        line2 = Vector_Sub(triTransformed.p[2], triTransformed.p[0])

        
        normal = Vector_CrossProduct(line1, line2)
        normal = Vector_Normalise(normal)
        if normal == vec3d(0, 0, 0):
            continue
            

        # naslednji del kode se izvede le, če lahko vidimo trikotnik

        if Vector_DotProduct(normal, Vector_Sub(triTransformed.p[0], vCamera)) < 0:
            light_direction = vec3d(0, 0, -1)
            light_direction = Vector_Normalise(light_direction)
            
            
            #podobnost(dot product) med normalo ploskve(pravokoten vektor) in smerjo 
            #svetlone(ki sicer kaže proti igralcu za lažji račun)
            dp = Vector_DotProduct(light_direction, normal)
            
            #UPOŠTEVANJE POLOŽAJA KAMERE PRI PROJEKCIJI
            triViewed.p[0] = Matrix_MulitplyVector(matView, triTransformed.p[0])
            triViewed.p[1] = Matrix_MulitplyVector(matView, triTransformed.p[1])
            triViewed.p[2] = Matrix_MulitplyVector(matView, triTransformed.p[2])
          
            
            #PROJEKCIJA 3D --> 2D
            triProjected.p[0] = Matrix_MulitplyVector(matProj, triViewed.p[0])
            triProjected.p[1] = Matrix_MulitplyVector(matProj, triViewed.p[1])
            triProjected.p[2] = Matrix_MulitplyVector(matProj, triViewed.p[2])
            
            triProjected.midpoint = (triProjected.p[0].z + triProjected.p[1].z + triProjected.p[2].z) / 3
            triProjected.color = GetColor(dp, (0, 0, 0), (255,255,255), bias = 1) #no bias
            
            #NORMALIZACIJA PROJEKCIJE
            triProjected.p[0] = Vector_Div(triProjected.p[0], triTransformed.p[0].w)
            triProjected.p[1] = Vector_Div(triProjected.p[1], triTransformed.p[1].w)
            triProjected.p[2] = Vector_Div(triProjected.p[2], triTransformed.p[2].w)
            
            
            # Povečava in premik na enkranu
            vOffsetView = vec3d(1, 1, 0)
            triProjected.p[0] = Vector_Add(triProjected.p[0], vOffsetView)
            triProjected.p[1] = Vector_Add(triProjected.p[1], vOffsetView)
            triProjected.p[2] = Vector_Add(triProjected.p[2], vOffsetView)
            
            triProjected.p[0].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[0].y *= 0.5 * SCREEN_HEIGHT
            triProjected.p[1].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[1].y *= 0.5 * SCREEN_HEIGHT
            triProjected.p[2].x *= 0.5 * SCREEN_WIDTH
            triProjected.p[2].y *= 0.5 * SCREEN_HEIGHT
            
            
            #Risanje trikotnikov, ki niso pokriti
            
            vecTrianglesToRaster.append(triProjected) 
 
        
    newList = sorted(vecTrianglesToRaster, key=lambda trik: -trik.midpoint) #tam je minus ker želim, da sortira od največjega do najmanjšega
    
    i = 1        
    for triProjected in newList:
        DrawTriangle(triProjected.p[0].x, triProjected.p[0].y, triProjected.p[1].x, triProjected.p[1].y, triProjected.p[2].x, triProjected.p[2].y, triProjected.color, drawEdge = False)  

    pygame.display.update()
    
    for event in pygame.event.get():
        if event == pygame.QUIT:
            running = False

pygame.quit()