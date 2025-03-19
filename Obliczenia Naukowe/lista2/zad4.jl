# Paweł Kędzierski 272400

import Pkg
Pkg.add("Polynomials")
using Polynomials

# Wspolczynniki wielomianu z zadania 3
coef::Vector{Float64} = [1, -210.0, 20615.0,-1256850.0,
                        53327946.0,-1672280820.0, 40171771630.0, -756111184500.0,          
                        11310276995381.0, -135585182899530.0,
                        1307535010540395.0,     -10142299865511450.0,
                        63030812099294896.0,     -311333643161390640.0,
                        1206647803780373360.0,     -3599979517947607200.0,
                        8037811822645051776.0,      -12870931245150988800.0,
                        13803759753640704000.0,      -8752948036761600000.0,
                        2432902008176640000.0]


my_poly::Polynomial = Polynomial(reverse(coef))
println("Polynomial: \n")
println(my_poly, "\n")


my_poly_roots::Vector{Float64} = roots(my_poly)

wilkinsons_poly::Polynomial = fromroots(my_poly_roots)
println(wilkinsons_poly, "\n")

println("Results for polynomial a: k --- z_k --- Pz_k --- pz_k --- diff\n")

for i::Int64 in 1:20
    z_k::Float64 = my_poly_roots[i]
    Pz_k::Float64 = abs(my_poly(z_k))
    pz_k::Float64 = abs(wilkinsons_poly(z_k))
    diff::Float64 = abs(z_k - i)
    println(i, " --- ", z_k, " --- ", Pz_k, " --- ", pz_k, " --- ", diff)
end



wil_coef::Vector{Float64} = [1, -210.0-(2)^(-23), 20615.0,-1256850.0,
                        53327946.0,-1672280820.0, 40171771630.0, -756111184500.0,          
                        11310276995381.0, -135585182899530.0,
                        1307535010540395.0,     -10142299865511450.0,
                        63030812099294896.0,     -311333643161390640.0,
                        1206647803780373360.0,     -3599979517947607200.0,
                        8037811822645051776.0,      -12870931245150988800.0,
                        13803759753640704000.0,      -8752948036761600000.0,
                        2432902008176640000.0]


my_poly_b::Polynomial = Polynomial(reverse(wil_coef))
println("Polynomial: \n")
println(my_poly_b)


my_poly_roots_b::Vector{ComplexF64} = roots(my_poly_b)


wilkinsons_poly_b::Polynomial = fromroots(my_poly_roots_b)
println(wilkinsons_poly_b, "\n")

println("Results for polynomial b: k --- z_k --- Pz_k --- pz_k --- diff\n")

for i::Int64 in 1:20
    z_k::ComplexF64 = my_poly_roots_b[i]
    Pz_k::Float64 = abs(my_poly_b(z_k))
    pz_k::Float64 = abs(wilkinsons_poly_b(z_k))
    diff::Float64 = abs(z_k - i)
    println(i, " --- ", z_k, " --- ", Pz_k, " --- ", pz_k, " --- ", diff)
end