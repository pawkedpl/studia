# Paweł Kędzierski

module interpolation

using Plots
    """
    Calculates divided differences calculated using the expanded form\n
        Arguments:
            x: knot vector
            f: function values vector
        Returns:
            fx: divided differences vector
    """
    function ilorazyRoznicowe(x::Vector{Float64}, f::Vector{Float64})
        x_length = size(x)[1]
        fx = Vector{Float64}(undef, x_length)
        for i = 1:x_length
            summ = 0
            for j = 1:i
                iloraz = 1
                for k = 1:i
                    if(j != k)
                        iloraz *= x[j] - x[k]
                    end  
                end
                summ += f[j] / iloraz
            end
            fx[i] = summ
        end
        return fx
    end

    """
    Calculates value of function in point t\n
        Arguments:
            x: knot vector
            fx: divided differences vector
            t: chosen x
        Returns:
            nt: value of the function in point t
    """
    function warNewton(x::Vector{Float64}, fx::Vector{Float64}, t::Float64)
        n = length(x) - 1
        w = Vector{Float64}(undef, n + 1)
        w[n+1] = fx[n + 1]

        for i in n:-1:1
            w[i] = fx[i] + (t - x[i]) * w[i + 1]
        end
        return w[1]
    end

    """
    Calculates the natural form of a function using knots and divided differences\n
        Arguments:
            x: knot vector
            fx: divided differences vector
        Returns:
            a: coeffitiens vector of the natural form of the function
    """
    function naturalna(x::Vector{Float64}, fx::Vector{Float64})
        n = length(fx) - 1
        a = Vector{Float64}(undef, n + 1)
        a[n + 1] = x[n + 1]

        for k in n:-1:1
            a[k] = fx[k] - a[k + 1] * (x[k] - x[k + 1])
        end

        return a
    end

    """
    Plots f(x) and it's interpolation
        Arguments:
            f: f(x)
            a, b: range of interpolation
            n: degree of the polynomial
        Returns:
            nothing
    """
    function rysujNnfx(f, a::Float64, b::Float64, n::Int)

        # calculating knots
        x = Vector{Float64}(undef, n + 1)   # knots
        h = (b - a) / n
        for k = 0:n
            x[k+1] = a + k * h
        end
        # calculating f(x)
        y = Vector{Float64}(undef, n + 1)
        for i = 1:n+1
            y[i] = f(x[i])
        end

        fx = ilorazyRoznicowe(x, y)

        # plotting
        point_number = 1000
        func_x = range(a, b, length=point_number)
        func_y = f.(func_x)
        interp_y = Vector{Float64}(undef, point_number)
        
        for i = 1:point_number
            interp_y[i] = warNewton(x, fx, func_x[i])
        end
        
        plot(func_x, [func_y, interp_y], labels=["f(x)" "interpolated function"])
        savefig("plot.png")
    end
end


