# Paweł Kędzierski

include("interpolation.jl")
# using .interpolation
using Plots

func(x::Float64) = sin(x)

# test knots
x = [0.0, 2.0, 3.0, 5.0, 6.0]
# test values of function in knots
f = [0.0, 8.0, 27.0, 125.0, 216.0]
t = 3.3
a = -10.0
b = 10.0
n = 10

# testing functions
fx = interpolation.ilorazyRoznicowe(x, f)
nt = interpolation.warNewton(x, fx, t)
nat = interpolation.naturalna(x, fx)
# interpolation.rysujNnfx(func, a, b, n)

println("Zad 1")
println("x = ", x)
println("f = ", f)
println("fx = ", fx)
println()
println("Zad 2")
println("x = ", x)
println("fx = ", fx)
println("t = ", t)
println("nt = ", nt)
println()
println("Zad 3")
println("x = ", x)
println("fx = ", fx)
println("a = ", nat)
println()
println("Zad 4")
println("plot saved as plot.png")
println()
println("Zad 5")
func5a(x) = ℯ^x
# interpolation.rysujNnfx(func5a, 0.0, 1.0, 15)
func5b(x) = x^2 * sin(x)
# interpolation.rysujNnfx(func5b, -1.0, 1.0, 15)
func6a(x) = abs(x)
# interpolation.rysujNnfx(func6a, -1.0, 1.0, 15)
func6b(x) = 1 / (1 + x^2)
interpolation.rysujNnfx(func6b, -5.0, 5.0, 15)

