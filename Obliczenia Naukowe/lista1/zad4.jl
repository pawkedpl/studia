# Pawel Kedzierski 272400
# parametry funkcji:
#   a - początek przedziału
#   b - koniec przedzialu
#   T - typ zmiennoprzecinkowy

function find_float(a, b, T) 
    x = nextfloat(T(a))
    res = 0.0

    while x < T(b) 
        res =  x * ( one(T) / x) 
        if res != 1
            return x
        end
        x = nextfloat(x)
    end

    return -1
end

println("Moje: ", find_float(1, 2, Float64))
