# Pawel Kedzierski 272400

# parametry funkcji:
#   x - wektor x
#   y - wektor y

function a(x, y)
    len = length(x)
    S = 0.0
    for i in 1:len
        S += x[i] * y[i]
    end
    
    return S
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y

function b(x, y)

    len = length(x)
    S = 0.0
    for i in len:-1:1 # specyfying the negative step
        S += x[i] * y[i]
    end

    return S
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y
#   T - typ zmiennoprzecinkowy

function c(x, y, T)

    len = length(x)
    S = Vector{T}(undef, len)

    for i in 1:len
        S[i] = x[i] * y[i]
    end

    S_pos = S[S .>= 0]
    S_neg = S[S .< 0]

    sort!(S_pos, rev=true)
    sort!(S_neg)

    sum_pos = 0.0
    for i in 1:length(S_pos)
        sum_pos += S_pos[i]
    end

    sum_neg = 0.0
    for i in 1:length(S_neg)
        sum_neg += S_neg[i]
    end

    return sum_pos + sum_neg
end

# parametry funkcji:
#   x - wektor x
#   y - wektor y
#   T - typ zmiennoprzecinkowy

function d(x, y, T)

    len = length(x)
    S = Vector{T}(undef, len)

    for i in 1:len
        S[i] = x[i] * y[i]
    end

    S_pos = S[S .>= 0]
    S_neg = S[S .< 0]

    sort!(S_pos)
    sort!(S_neg, rev=true)

    sum_pos = 0.0
    for i in 1:length(S_pos)
        sum_pos += S_pos[i]
    end

    sum_neg = 0.0
    for i in 1:length(S_neg)
        sum_neg += S_neg[i]
    end

    return sum_pos + sum_neg
end

x_32::Vector{Float32} = [2.718281828, −3.141592654, 1.414213562, 0.5772156649, 0.3010299957]
y_32::Vector{Float32} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

x_64::Vector{Float64} = [2.718281828, −3.141592654, 1.414213562, 0.5772156649, 0.3010299957]
y_64::Vector{Float64} = [1486.2497, 878366.9879, −22.37492, 4773714.647, 0.000185049]

println("For Float32: a --- b --- c --- d")
println(a(x_32, y_32), " --- ", b(x_32, y_32), " --- ", c(x_32, y_32, Float32), " --- ", d(x_32, y_32, Float32))
println("\nFor Float64: a --- b --- c --- d")
println(a(x_64, y_64), " --- ", b(x_64, y_64), " --- ", c(x_64, y_64, Float64), " --- ", d(x_64, y_64, Float64))
